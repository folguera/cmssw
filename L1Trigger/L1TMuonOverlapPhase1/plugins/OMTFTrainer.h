#ifndef OMTFTrainer_H
#define OMTFTrainer_H

#include "L1Trigger/L1TMuonOverlapPhase1/interface/Omtf/OMTFReconstruction.h"

#include "xercesc/util/XercesDefs.hpp"

#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Framework/interface/EDProducer.h"

#include "DataFormats/L1DTTrackFinder/interface/L1MuDTChambPhContainer.h"
#include "DataFormats/L1DTTrackFinder/interface/L1MuDTChambThContainer.h"
#include "DataFormats/CSCDigi/interface/CSCCorrelatedLCTDigiCollection.h"
#include "DataFormats/RPCDigi/interface/RPCDigiCollection.h"
#include "SimDataFormats/Track/interface/SimTrackContainer.h"

#include "DataFormats/L1TMuon/interface/RegionalMuonCandFwd.h"

#include <TH1.h>

class OMTFConfiguration;
class OMTFConfigMaker;
class OMTFinputMaker;

class SimTrack;

class XMLConfigWriter;

namespace XERCES_CPP_NAMESPACE {
  class DOMElement;
  class DOMDocument;
  class DOMImplementation;
}  // namespace XERCES_CPP_NAMESPACE

class OMTFTrainer : public edm::EDProducer {
public:
  OMTFTrainer(const edm::ParameterSet& cfg);

  ~OMTFTrainer() override;

  void beginRun(edm::Run const& run, edm::EventSetup const& iSetup) override;

  void beginJob() override;

  void endJob() override;

  void produce(edm::Event&, const edm::EventSetup&) override;

private:
  // const SimTrack *findSimMuon(const edm::Event &ev, const edm::EventSetup &es, const SimTrack *previous=0);

  edm::ParameterSet theConfig;
  edm::InputTag g4SimTrackSrc;

  edm::EDGetTokenT<edm::SimTrackContainer> inputTokenSimHit;

  MuStubsInputTokens muStubsInputTokens;

  OMTFReconstruction m_Reconstruction;

  TH1I* ptDist;

  double etaCutFrom = 0;
  double etaCutTo = 0;
};

#endif
