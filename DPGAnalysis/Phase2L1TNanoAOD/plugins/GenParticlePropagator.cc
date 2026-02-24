#include "FWCore/Framework/interface/global/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/StreamID.h"
#include "FWCore/Utilities/interface/ESGetToken.h"

#include "DataFormats/HepMCCandidate/interface/GenParticle.h"
#include "DataFormats/HepMCCandidate/interface/GenParticleFwd.h"
#include "DataFormats/Common/interface/ValueMap.h"

#include "MuonAnalysis/MuonAssociators/interface/PropagateToMuonSetup.h"
#include "TrackingTools/TrajectoryState/interface/TrajectoryStateOnSurface.h"
#include "TrackingTools/TrajectoryState/interface/FreeTrajectoryState.h"
#include "TrackingTools/TrajectoryParametrization/interface/GlobalTrajectoryParameters.h"
#include "TrackingTools/TrajectoryParametrization/interface/CurvilinearTrajectoryError.h"
#include "MagneticField/Engine/interface/MagneticField.h"
#include "MagneticField/Records/interface/IdealMagneticFieldRecord.h"
#include "DataFormats/GeometryVector/interface/GlobalPoint.h"
#include "DataFormats/GeometryVector/interface/GlobalVector.h"

#include <memory>
#include <vector>
#include <cmath>

class GenParticlePropagator : public edm::global::EDProducer<> {
public:
  explicit GenParticlePropagator(const edm::ParameterSet&);
  ~GenParticlePropagator() override = default;

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

private:
  void produce(edm::StreamID, edm::Event&, const edm::EventSetup&) const override;

  // Tokens
  edm::EDGetTokenT<reco::GenParticleCollection> srcToken_;
  edm::ESGetToken<MagneticField, IdealMagneticFieldRecord> magFieldToken_;

  // Propagadores a estaciones de muones
  const PropagateToMuonSetup muPropagatorSetup1st_;
  const PropagateToMuonSetup muPropagatorSetup2nd_;
};

GenParticlePropagator::GenParticlePropagator(const edm::ParameterSet& iConfig)
    : srcToken_(consumes<reco::GenParticleCollection>(iConfig.getParameter<edm::InputTag>("src"))),
      magFieldToken_(esConsumes()),
      muPropagatorSetup1st_(iConfig.getParameter<edm::ParameterSet>("muProp1st"), consumesCollector()),
      muPropagatorSetup2nd_(iConfig.getParameter<edm::ParameterSet>("muProp2nd"), consumesCollector()) {
  
  produces<edm::ValueMap<float>>("etaSt1");
  produces<edm::ValueMap<float>>("phiSt1");
  produces<edm::ValueMap<float>>("etaSt2");
  produces<edm::ValueMap<float>>("phiSt2");
}

void GenParticlePropagator::produce(edm::StreamID, edm::Event& iEvent, const edm::EventSetup& iSetup) const {
  auto genParticles = iEvent.getHandle(srcToken_);

  // Inicializar propagadores
  PropagateToMuon muPropagator1st = muPropagatorSetup1st_.init(iSetup);
  PropagateToMuon muPropagator2nd = muPropagatorSetup2nd_.init(iSetup);
  
  // Obtener campo magnético
  const auto& magField = iSetup.getData(magFieldToken_);

  std::vector<float> etaSt1_vals, phiSt1_vals;
  std::vector<float> etaSt2_vals, phiSt2_vals;

  for (const auto& gp : *genParticles) {
    // Filtrar: solo muones última copia
    if (std::abs(gp.pdgId()) != 13 || !gp.statusFlags().isLastCopy()) {
      etaSt1_vals.push_back(-999.f);
      phiSt1_vals.push_back(-999.f);
      etaSt2_vals.push_back(-999.f);
      phiSt2_vals.push_back(-999.f);
      continue;
    }

    // Validar momentum mínimo
    if (gp.pt() < 0.5) {
      etaSt1_vals.push_back(-999.f);
      phiSt1_vals.push_back(-999.f);
      etaSt2_vals.push_back(-999.f);
      phiSt2_vals.push_back(-999.f);
      continue;
    }

    // Construir FreeTrajectoryState manualmente desde GenParticle
    GlobalPoint vtx(gp.vx(), gp.vy(), gp.vz());
    GlobalVector mom(gp.px(), gp.py(), gp.pz());
    int charge = gp.charge();
    
    // Si la carga es 0 (puede pasar con GenParticles), inferir desde PDG
    if (charge == 0) {
      charge = (gp.pdgId() > 0) ? -1 : 1; // mu- tiene charge -1, mu+ tiene charge +1
    }
    
    GlobalTrajectoryParameters gtp(vtx, mom, charge, &magField);
    
    // Matriz de covarianza (errores pequeños)
    AlgebraicSymMatrix55 errorMatrix = AlgebraicSymMatrix55();
    errorMatrix(0,0) = 1e-6;  // error en q/p
    errorMatrix(1,1) = 1e-6;  // error en lambda (dip angle)
    errorMatrix(2,2) = 1e-6;  // error en phi
    errorMatrix(3,3) = 1e-6;  // error en x
    errorMatrix(4,4) = 1e-6;  // error en y
    
    CurvilinearTrajectoryError cte(errorMatrix);
    FreeTrajectoryState fts(gtp, cte);
    
    // Propagar a primera estación de muones
    TrajectoryStateOnSurface stateAtSt1 = muPropagator1st.extrapolate(fts);
    if (stateAtSt1.isValid()) {
      etaSt1_vals.push_back(stateAtSt1.globalPosition().eta());
      phiSt1_vals.push_back(stateAtSt1.globalPosition().phi());
    } else {
      etaSt1_vals.push_back(-999.f);
      phiSt1_vals.push_back(-999.f);
    }

    // Propagar a segunda estación de muones
    TrajectoryStateOnSurface stateAtSt2 = muPropagator2nd.extrapolate(fts);
    if (stateAtSt2.isValid()) {
      etaSt2_vals.push_back(stateAtSt2.globalPosition().eta());
      phiSt2_vals.push_back(stateAtSt2.globalPosition().phi());
    } else {
      etaSt2_vals.push_back(-999.f);
      phiSt2_vals.push_back(-999.f);
    }
  }

  // Crear ValueMaps
  auto makeValueMap = [&genParticles, &iEvent](const std::vector<float>& vals, const std::string& name) {
    auto vMap = std::make_unique<edm::ValueMap<float>>();
    edm::ValueMap<float>::Filler filler(*vMap);
    filler.insert(genParticles, vals.begin(), vals.end());
    filler.fill();
    iEvent.put(std::move(vMap), name);
  };

  makeValueMap(etaSt1_vals, "etaSt1");
  makeValueMap(phiSt1_vals, "phiSt1");
  makeValueMap(etaSt2_vals, "etaSt2");
  makeValueMap(phiSt2_vals, "phiSt2");
}

void GenParticlePropagator::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  edm::ParameterSetDescription desc;
  desc.add<edm::InputTag>("src", edm::InputTag("finalGenParticles"));

  // Muon track extrapolation to 1st station
  edm::ParameterSetDescription muProp1st;
  muProp1st.add<std::string>("useTrack", "tracker");
  muProp1st.add<std::string>("useState", "atVertex");
  muProp1st.add<bool>("useSimpleGeometry", true);
  muProp1st.add<bool>("useStation2", false);
  muProp1st.add<bool>("fallbackToME1", false);
  muProp1st.add<bool>("cosmicPropagationHypothesis", false);
  muProp1st.add<bool>("useMB2InOverlap", false);
  muProp1st.add<edm::ESInputTag>("propagatorAlong", edm::ESInputTag("", "SteppingHelixPropagatorAlong"));
  muProp1st.add<edm::ESInputTag>("propagatorAny", edm::ESInputTag("", "SteppingHelixPropagatorAny"));
  muProp1st.add<edm::ESInputTag>("propagatorOpposite", edm::ESInputTag("", "SteppingHelixPropagatorOpposite"));
  desc.add<edm::ParameterSetDescription>("muProp1st", muProp1st);

  // Muon track extrapolation to 2nd station
  edm::ParameterSetDescription muProp2nd;
  muProp2nd.add<std::string>("useTrack", "none");
  muProp2nd.add<std::string>("useState", "atVertex");
  muProp2nd.add<bool>("useSimpleGeometry", false);
  muProp2nd.add<bool>("useStation2", true);
  muProp2nd.add<bool>("fallbackToME1", false);
  muProp2nd.add<bool>("cosmicPropagationHypothesis", false);
  muProp2nd.add<bool>("useMB2InOverlap", true);
  muProp2nd.add<edm::ESInputTag>("propagatorAlong", edm::ESInputTag("", "SteppingHelixPropagatorAlong"));
  muProp2nd.add<edm::ESInputTag>("propagatorAny", edm::ESInputTag("", "SteppingHelixPropagatorAny"));
  muProp2nd.add<edm::ESInputTag>("propagatorOpposite", edm::ESInputTag("", "SteppingHelixPropagatorOpposite"));
  desc.add<edm::ParameterSetDescription>("muProp2nd", muProp2nd);

  descriptions.add("GenParticlePropagator", desc);
}

DEFINE_FWK_MODULE(GenParticlePropagator);