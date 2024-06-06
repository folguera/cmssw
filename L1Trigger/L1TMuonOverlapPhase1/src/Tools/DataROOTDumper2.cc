/*
 * DataROOTDumper2.cc
 *
 *  Created on: Dec 11, 2019
 *      Author: kbunkow
 */

#include "L1Trigger/L1TMuonOverlapPhase1/interface/Tools/DataROOTDumper2.h"

#include "CommonTools/UtilAlgos/interface/TFileService.h"
#include "FWCore/ServiceRegistry/interface/Service.h"

#include "FWCore/MessageLogger/interface/MessageLogger.h"
#include "DataFormats/MuonDetId/interface/CSCDetId.h"
#include "DataFormats/MuonDetId/interface/RPCDetId.h"
#include "DataFormats/MuonDetId/interface/DTChamberId.h"
#include "DataFormats/MuonDetId/interface/MuonSubdetId.h"

#include "TFile.h"
#include "TTree.h"

DataROOTDumper2::DataROOTDumper2(const edm::ParameterSet& edmCfg,
                                 const OMTFConfiguration* omtfConfig,
                                 CandidateSimMuonMatcher* candidateSimMuonMatcher)
    : EmulationObserverBase(edmCfg, omtfConfig), candidateSimMuonMatcher(candidateSimMuonMatcher), inputInProcs(omtfConfig->processorCnt()) {
  edm::LogVerbatim("l1tOmtfEventPrint") << " omtfConfig->nTestRefHits() " << omtfConfig->nTestRefHits()
                                        << " event.omtfGpResultsPdfSum.num_elements() " << endl;
  initializeTTree();

  if (edmCfg.exists("dumpKilledOmtfCands"))
    if (edmCfg.getParameter<bool>("dumpKilledOmtfCands"))
      dumpKilledOmtfCands = true;

  if (edmCfg.exists("candidateSimMuonMatcherType")) {
    if (edmCfg.getParameter<std::string>("candidateSimMuonMatcherType") == "propagation")
      usePropagation = true;
    else if (edmCfg.getParameter<std::string>("candidateSimMuonMatcherType") == "matchSimple")
      usePropagation = false;

    edm::LogImportant("l1tOmtfEventPrint")
        << " CandidateSimMuonMatcher: candidateSimMuonMatcherType "
        << edmCfg.getParameter<std::string>("candidateSimMuonMatcherType") << std::endl;
  }

  edm::LogVerbatim("l1tOmtfEventPrint") << " DataROOTDumper2 created. dumpKilledOmtfCands " << dumpKilledOmtfCands
                                        << std::endl;
}

DataROOTDumper2::~DataROOTDumper2() {}

void DataROOTDumper2::initializeTTree() {
  edm::Service<TFileService> fs;

  rootTree = fs->make<TTree>("OMTFHitsTree", "");

  rootTree->Branch("eventNum", &omtfEvent.eventNum);
  rootTree->Branch("muonEvent", &omtfEvent.muonEvent);

  rootTree->Branch("muonPt", &omtfEvent.muonPt);
  rootTree->Branch("muonEta", &omtfEvent.muonEta);
  rootTree->Branch("muonPhi", &omtfEvent.muonPhi);
  rootTree->Branch("muonPropEta", &omtfEvent.muonPropEta);
  rootTree->Branch("muonPropPhi", &omtfEvent.muonPropPhi);
  rootTree->Branch("muonCharge", &omtfEvent.muonCharge);

  rootTree->Branch("muonDxy", &omtfEvent.muonDxy);
  rootTree->Branch("muonRho", &omtfEvent.muonRho);

  rootTree->Branch("omtfPt", &omtfEvent.omtfPt);
  rootTree->Branch("omtfUPt", &omtfEvent.omtfUPt);
  rootTree->Branch("omtfEta", &omtfEvent.omtfEta);
  rootTree->Branch("omtfPhi", &omtfEvent.omtfPhi);
  rootTree->Branch("omtfCharge", &omtfEvent.omtfCharge);

  rootTree->Branch("omtfHwEta", &omtfEvent.omtfHwEta);

  rootTree->Branch("omtfProcessor", &omtfEvent.omtfProcessor);
  rootTree->Branch("omtfScore", &omtfEvent.omtfScore);
  rootTree->Branch("omtfQuality", &omtfEvent.omtfQuality);
  rootTree->Branch("omtfRefLayer", &omtfEvent.omtfRefLayer);
  rootTree->Branch("omtfRefHitNum", &omtfEvent.omtfRefHitNum);

  rootTree->Branch("omtfFiredLayers", &omtfEvent.omtfFiredLayers);  //<<<<<<<<<<<<<<<<<<<<<<!!!!TODOO

  rootTree->Branch("killed", &omtfEvent.killed);

  rootTree->Branch("stubNo", &omtfEvent.stubNo);
  rootTree->Branch("stubLayer", &omtfEvent.stubLayer);
  rootTree->Branch("stubQuality", &omtfEvent.stubQuality);
  rootTree->Branch("stubZ", &omtfEvent.stubZ);
  rootTree->Branch("stubValid", &omtfEvent.stubValid);
  rootTree->Branch("stubEta", &omtfEvent.stubEta);
  rootTree->Branch("stubPhiDist", &omtfEvent.stubPhiDist);
  rootTree->Branch("stubEtaDist", &omtfEvent.stubEtaDist);
  rootTree->Branch("stubPhi", &omtfEvent.stubPhi);
  rootTree->Branch("stubIsRefLayer", &omtfEvent.stubIsRefLayer);
  rootTree->Branch("stubTiming", &omtfEvent.stubTiming);
  rootTree->Branch("stubDetId", &omtfEvent.stubDetId);
  rootTree->Branch("stubBx", &omtfEvent.stubBx);
  rootTree->Branch("stubPhiB", &omtfEvent.stubPhiB);
  rootTree->Branch("stubR", &omtfEvent.stubR);
  rootTree->Branch("stubType", &omtfEvent.stubType);

  rootTree->Branch("inputStubNo", &omtfEvent.inputStubNo);
  rootTree->Branch("inputStubLogicLayer", &omtfEvent.inputStubLogicLayer);
  rootTree->Branch("inputStubProc", &omtfEvent.inputStubProc);
  rootTree->Branch("inputStubPhi", &omtfEvent.inputStubPhi);
  rootTree->Branch("inputStubPhiB", &omtfEvent.inputStubPhiB);
  rootTree->Branch("inputStubEta", &omtfEvent.inputStubEta);
  rootTree->Branch("inputStubQuality", &omtfEvent.inputStubQuality);
  rootTree->Branch("inputStubBx", &omtfEvent.inputStubBx);
  rootTree->Branch("inputStubTiming", &omtfEvent.inputStubTiming);
  rootTree->Branch("inputStubDetId", &omtfEvent.inputStubDetId);
  rootTree->Branch("inputStubType", &omtfEvent.inputStubType); 
  rootTree->Branch("inputStubIsMatched", &omtfEvent.inputStubIsMatched);  
//  rootTree->Branch("inputStubIsRefLayer", &omtfEvent.inputStubIsRefLayer);
  rootTree->Branch("inputStubDeltaPhi0", &omtfEvent.inputStubDeltaPhi0);
  rootTree->Branch("inputStubDeltaPhi1", &omtfEvent.inputStubDeltaPhi1);
  rootTree->Branch("inputStubDeltaPhi2", &omtfEvent.inputStubDeltaPhi2);
  rootTree->Branch("inputStubDeltaPhi3", &omtfEvent.inputStubDeltaPhi3);
  rootTree->Branch("inputStubDeltaPhi4", &omtfEvent.inputStubDeltaPhi4);
  rootTree->Branch("inputStubDeltaPhi5", &omtfEvent.inputStubDeltaPhi5);
  rootTree->Branch("inputStubDeltaPhi6", &omtfEvent.inputStubDeltaPhi6);
  rootTree->Branch("inputStubDeltaPhi7", &omtfEvent.inputStubDeltaPhi7);
  rootTree->Branch("inputStubDeltaEta0", &omtfEvent.inputStubDeltaEta0);
  rootTree->Branch("inputStubDeltaEta1", &omtfEvent.inputStubDeltaEta1);
  rootTree->Branch("inputStubDeltaEta2", &omtfEvent.inputStubDeltaEta2);
  rootTree->Branch("inputStubDeltaEta3", &omtfEvent.inputStubDeltaEta3);
  rootTree->Branch("inputStubDeltaEta4", &omtfEvent.inputStubDeltaEta4);
  rootTree->Branch("inputStubDeltaEta5", &omtfEvent.inputStubDeltaEta5);
  rootTree->Branch("inputStubDeltaEta6", &omtfEvent.inputStubDeltaEta6);
  rootTree->Branch("inputStubDeltaEta7", &omtfEvent.inputStubDeltaEta7);
  
  rootTree->Branch("deltaEta", &omtfEvent.deltaEta);
  rootTree->Branch("deltaPhi", &omtfEvent.deltaPhi);

  ptGenPos = fs->make<TH1I>("ptGenPos", "ptGenPos, eta at vertex 0.8 - 1.24", 400, 0, 200);  //TODO
  ptGenNeg = fs->make<TH1I>("ptGenNeg", "ptGenNeg, eta at vertex 0.8 - 1.24", 400, 0, 200);
}

void DataROOTDumper2::observeEventBegin(const edm::Event& iEvent) {
  clearOmtfInputStubs();
  clearOmtfStubs();
  for (auto& input : inputInProcs)
    input.reset();
  
}

void DataROOTDumper2::observeProcesorEmulation(unsigned int iProcessor,
                                               l1t::tftype mtfType,
                                               const std::shared_ptr<OMTFinput>& input,
                                               const AlgoMuons& algoCandidates,
                                               const AlgoMuons& gbCandidates,
                                               const std::vector<l1t::RegionalMuonCand>& candMuons) {

  unsigned int procIndx = omtfConfig->getProcIndx(iProcessor, mtfType);
  inputInProcs[procIndx] = input;
}

void DataROOTDumper2::observeEventEnd(const edm::Event& iEvent,
                                      std::unique_ptr<l1t::RegionalMuonCandBxCollection>& finalCandidates) {
  /*
  int muonCharge = 0;
  if (simMuon) {
    if (std::abs(simMuon->momentum().eta()) < 0.8 || std::abs(simMuon->momentum().eta()) > 1.24)
      return;

    muonCharge = (std::abs(simMuon->type()) == 13) ? simMuon->type() / -13 : 0;
    if (muonCharge > 0)
      ptGenPos->Fill(simMuon->momentum().pt());
    else
      ptGenNeg->Fill(simMuon->momentum().pt());
  }

  if (simMuon == nullptr || !omtfCand->isValid())  //no sim muon or empty candidate
    return;

  omtfEvent.muonPt = simMuon->momentum().pt();
  omtfEvent.muonEta = simMuon->momentum().eta();

  //TODO add cut on ete if needed
    if(std::abs(event.muonEta) < 0.8 || std::abs(event.muonEta) > 1.24)
    return;

  omtfEvent.muonPhi = simMuon->momentum().phi();
  omtfEvent.muonCharge = muonCharge;  //TODO
   */

  std::vector<MatchingResult> matchingResults = candidateSimMuonMatcher->getMatchingResults();
  LogTrace("l1tOmtfEventPrint") << "\nDataROOTDumper2::observeEventEnd matchingResults.size() "
                                << matchingResults.size() << std::endl;

  //candidateSimMuonMatcher should use the  trackingParticles, because the simTracks are not stored for the pile-up events

  //for some events there are more than one matchingResults,
  //Usually at least one them has  genPt 0, which means no simMuon was matched, so candidate is ghost (or fake)
  //so better is to to drop such event, as it is not sue if the correct simMuon was matched to the candidate.
  //So we assume here that when the propagation is not used it is a single mu sample and this filter has sense
  //the propagation is used for multi-muon sample, so then this fitler cannot be used
  //TODO add a flag to enable this filter? Disable it if not needed
  if (!usePropagation && matchingResults.size() > 1) {  //omtfConfig->cleanStubs() &&
    edm::LogVerbatim("l1tOmtfEventPrint")
        << "\nDataROOTDumper2::observeEventEnd matchingResults.size() " << matchingResults.size() << std::endl;

    for (auto& matchingResult : matchingResults) {
      edm::LogVerbatim("l1tOmtfEventPrint") << "matchingResult: genPt " << matchingResult.genPt;
      if (matchingResult.procMuon)
        edm::LogVerbatim("l1tOmtfEventPrint") << " procMuon.PtConstr " << matchingResult.procMuon->getPtConstr();
      else
        edm::LogVerbatim("l1tOmtfEventPrint") << " no procMuon" << std::endl;
    }
    edm::LogVerbatim("l1tOmtfEventPrint") << "dropping the event!!!\n" << std::endl;
    return;
  }

  for (auto& matchingResult : matchingResults) {
    omtfEvent.eventNum = iEvent.id().event();

    if (matchingResult.trackingParticle) {
      auto trackingParticle = matchingResult.trackingParticle;

      omtfEvent.muonEvent = trackingParticle->eventId().event();

      omtfEvent.muonPt = trackingParticle->pt();
      omtfEvent.muonEta = trackingParticle->momentum().eta();
      omtfEvent.muonPhi = trackingParticle->momentum().phi();
      omtfEvent.muonPropEta = matchingResult.propagatedEta;
      omtfEvent.muonPropPhi = matchingResult.propagatedPhi;
      omtfEvent.muonCharge = (std::abs(trackingParticle->pdgId()) == 13) ? trackingParticle->pdgId() / -13 : 0;

      if (trackingParticle->parentVertex().isNonnull()) {
        omtfEvent.muonDxy = trackingParticle->dxy();
        omtfEvent.muonRho = trackingParticle->parentVertex()->position().Rho();
      }

      omtfEvent.deltaEta = matchingResult.deltaEta;
      omtfEvent.deltaPhi = matchingResult.deltaPhi;

      LogTrace("l1tOmtfEventPrint") << "DataROOTDumper2::observeEventEnd trackingParticle: eventId "
                                    << trackingParticle->eventId().event() << " pdgId " << std::setw(3)
                                    << trackingParticle->pdgId() << " trackId "
                                    << trackingParticle->g4Tracks().at(0).trackId() << " pt " << std::setw(9)
                                    << trackingParticle->pt()  //<<" Beta "<<simMuon->momentum().Beta()
                                    << " eta " << std::setw(9) << trackingParticle->momentum().eta() << " phi "
                                    << std::setw(9) << trackingParticle->momentum().phi() << std::endl;

      if (std::abs(omtfEvent.muonEta) > 0.8 && std::abs(omtfEvent.muonEta) < 1.24) {
        if (omtfEvent.muonCharge > 0)
          ptGenPos->Fill(omtfEvent.muonPt);
        else
          ptGenNeg->Fill(omtfEvent.muonPt);
      }
    } else if (matchingResult.simTrack) {
      auto simTrack = matchingResult.simTrack;

      omtfEvent.muonEvent = simTrack->eventId().event();

      omtfEvent.muonPt = simTrack->momentum().pt();
      omtfEvent.muonEta = simTrack->momentum().eta();
      omtfEvent.muonPhi = simTrack->momentum().phi();
      omtfEvent.muonPropEta = matchingResult.propagatedEta;
      omtfEvent.muonPropPhi = matchingResult.propagatedPhi;
      omtfEvent.muonCharge = simTrack->charge();
      
      if (!simTrack->noVertex() && matchingResult.simVertex) {
        const math::XYZTLorentzVectorD& vtxPos = matchingResult.simVertex->position();
        omtfEvent.muonDxy = (-vtxPos.X() * simTrack->momentum().py() + vtxPos.Y() * simTrack->momentum().px()) /
                            simTrack->momentum().pt();
        omtfEvent.muonRho = vtxPos.Rho();
      }

      omtfEvent.deltaEta = matchingResult.deltaEta;
      omtfEvent.deltaPhi = matchingResult.deltaPhi;

      LogTrace("l1tOmtfEventPrint") << "DataROOTDumper2::observeEventEnd simTrack: eventId "
                                    << simTrack->eventId().event() << " pdgId " << std::setw(3)
                                    << simTrack->type()  //<< " trackId " << simTrack->g4Tracks().at(0).trackId()
                                    << " pt " << std::setw(9)
                                    << simTrack->momentum().pt()  //<<" Beta "<<simMuon->momentum().Beta()
                                    << " eta " << std::setw(9) << simTrack->momentum().eta() << " phi " << std::setw(9)
                                    << simTrack->momentum().phi() << std::endl;

      if (std::abs(omtfEvent.muonEta) > 0.8 && std::abs(omtfEvent.muonEta) < 1.24) {
        if (omtfEvent.muonCharge > 0)
          ptGenPos->Fill(omtfEvent.muonPt);
        else
          ptGenNeg->Fill(omtfEvent.muonPt);
      }
    } else {
      omtfEvent.muonEvent = -1;

      omtfEvent.muonPt = 0;

      omtfEvent.muonEta = 0;
      omtfEvent.muonPhi = 0;

      omtfEvent.muonPropEta = 0;
      omtfEvent.muonPropPhi = 0;

      omtfEvent.muonCharge = 0;  //TODO

      omtfEvent.muonDxy = 0;
      omtfEvent.muonRho = 0;
    }

    auto addOmtfCand = [&](AlgoMuonPtr& procMuon) {
      omtfEvent.omtfPt = omtfConfig->hwPtToGev(procMuon->getPtConstr());
      omtfEvent.omtfUPt = omtfConfig->hwUPtToGev(procMuon->getPtUnconstr());
      omtfEvent.omtfEta = omtfConfig->hwEtaToEta(procMuon->getEtaHw());
      omtfEvent.omtfPhi = procMuon->getPhi();
      omtfEvent.omtfCharge = procMuon->getChargeConstr();
      omtfEvent.omtfScore = procMuon->getPdfSum();

      omtfEvent.omtfHwEta = procMuon->getEtaHw();

      omtfEvent.omtfFiredLayers = procMuon->getFiredLayerBits();
      omtfEvent.omtfRefLayer = procMuon->getRefLayer();
      omtfEvent.omtfRefHitNum = procMuon->getRefHitNumber();

      clearOmtfStubs();
      clearOmtfInputStubs();

      //TODO choose, which gpResult should be dumped
      //auto& gpResult = procMuon->getGpResultConstr();
      auto& gpResult = (procMuon->getGpResultUnconstr().getPdfSumUnconstr() > procMuon->getGpResultConstr().getPdfSum())
                           ? procMuon->getGpResultUnconstr()
                           : procMuon->getGpResultConstr();


      for (unsigned int iLogicLayer = 0; iLogicLayer < gpResult.getStubResults().size(); ++iLogicLayer) {
        auto& stubResult = gpResult.getStubResults()[iLogicLayer];

        //TODO it is to have the hit if it is below the quality cut
        /*if (omtfConfigstubResult->isBendingLayer(iLogicLayer) && !stubResult.getMuonStub()) {
          auto&  = gpResult.getStubResults()[iLogicLayer-1];
        }*/

	if (omtfConfig->isBendingLayer(iLogicLayer)) continue; //layer = iLayer - 1;        
        if (stubResult.getMuonStub()) {  //&& stubResult.getValid() //TODO!!!!!!!!!!!!!!!!
          omtfEvent.stubNo++;
          omtfEvent.stubLayer.push_back(iLogicLayer);
          omtfEvent.stubQuality.push_back(stubResult.getMuonStub()->qualityHw);
          omtfEvent.stubValid.push_back(stubResult.getValid());

          int hitPhi = stubResult.getMuonStub()->phiHw;
          int hitEta = stubResult.getMuonStub()->etaHw;
          unsigned int refLayerLogicNum = omtfConfig->getRefToLogicNumber()[procMuon->getRefLayer()];
          int phiRefHit = gpResult.getStubResults()[refLayerLogicNum].getMuonStub()->phiHw;
          int etaRefHit = gpResult.getStubResults()[refLayerLogicNum].getMuonStub()->etaHw;

	  /*          if (omtfConfig->isBendingLayer(iLogicLayer)) {
            continue;
            hitPhi = stubResult.getMuonStub()->phiBHw;
            phiRefHit = 0;  //phi ref hit for the bending layer set to 0, since it should not be included in the phiDist
            etaRefHit = 0;  //eta ref hit for the bending layer set to 0, since it should not be included in the phiDist
          }
	  */
         
          omtfEvent.stubPhiDist.push_back(hitPhi - phiRefHit);
          omtfEvent.stubEtaDist.push_back(hitEta - etaRefHit);
          omtfEvent.stubPhi.push_back(hitPhi);
          omtfEvent.stubEta.push_back(hitEta);
          omtfEvent.stubIsRefLayer.push_back(iLogicLayer == refLayerLogicNum);
          omtfEvent.stubTiming.push_back(stubResult.getMuonStub()->timing);
          omtfEvent.stubDetId.push_back(stubResult.getMuonStub()->detId);
          omtfEvent.stubBx.push_back(stubResult.getMuonStub()->bx);
          omtfEvent.stubPhiB.push_back(stubResult.getMuonStub()->phiBHw);
          omtfEvent.stubR.push_back(stubResult.getMuonStub()->r);
          omtfEvent.stubType.push_back(stubResult.getMuonStub()->type);

          DetId detId(stubResult.getMuonStub()->detId);
          if (detId.subdetId() == MuonSubdetId::CSC) {
            CSCDetId cscId(detId);
            omtfEvent.stubZ.push_back(cscId.chamber() % 2);
          }
        }
      }

      LogTrace("l1tOmtfEventPrint") << "DataROOTDumper2::observeEventEnd adding omtfCand : " << std::endl;
      auto finalCandidate = matchingResult.muonCand;
      LogTrace("l1tOmtfEventPrint") << " hwPt " << finalCandidate->hwPt() << " hwSign " << finalCandidate->hwSign()
                                    << " hwQual " << finalCandidate->hwQual() << " hwEta " << std::setw(4)
                                    << finalCandidate->hwEta() << std::setw(4) << " hwPhi " << finalCandidate->hwPhi()
                                    << "    eta " << std::setw(9) << (finalCandidate->hwEta() * 0.010875)
                                    << " isKilled " << procMuon->isKilled() << " tRefLayer " << procMuon->getRefLayer()
                                    << " RefHitNumber " << procMuon->getRefHitNumber() << std::endl;
    };

    if (matchingResult.muonCand && matchingResult.procMuon->getPtConstr() > 0 &&
        matchingResult.muonCand->hwQual() >= 1) {
      //TODO set the quality, quality 0 has the candidates with eta > 1.3(?) EtaHw >= 121
      //&& matchingResult.genPt < 20

      omtfEvent.omtfQuality = matchingResult.muonCand->hwQual();  //procMuon->getQ();
      omtfEvent.killed = false;
      omtfEvent.omtfProcessor = matchingResult.muonCand->processor();

      if (matchingResult.muonCand->trackFinderType() == l1t::omtf_neg) {
        omtfEvent.omtfProcessor *= -1;
      }

      addOmtfCand(matchingResult.procMuon);
      addOmtfInputStubsFromProc(matchingResult.muonCand->processor(), matchingResult.muonCand->trackFinderType(), matchingResult.procMuon);
      rootTree->Fill();
      clearOmtfStubs();
      clearOmtfInputStubs();
      
      if (dumpKilledOmtfCands) {
        for (auto& killedCand : matchingResult.procMuon->getKilledMuons()) {
          omtfEvent.omtfQuality = 0;
          omtfEvent.killed = true;
          if (killedCand->isKilled() == false) {
            edm::LogVerbatim("l1tOmtfEventPrint") << " killedCand->isKilled() == false !!!!!!!!";
          }
          addOmtfCand(killedCand);
          rootTree->Fill();
          clearOmtfStubs();
          clearOmtfInputStubs();
        }
      }
    } else if (omtfEvent.muonPt > 0) {  //checking if there was a simMuon
      LogTrace("l1tOmtfEventPrint") << "DataROOTDumper2::observeEventEnd no matching omtfCand" << std::endl;

      omtfEvent.omtfPt = 0;
      omtfEvent.omtfUPt = 0;
      omtfEvent.omtfEta = 0;
      omtfEvent.omtfPhi = 0;
      omtfEvent.omtfCharge = 0;
      omtfEvent.omtfScore = 0;

      omtfEvent.omtfHwEta = 0;

      omtfEvent.omtfFiredLayers = 0;
      omtfEvent.omtfRefLayer = 0;
      omtfEvent.omtfRefHitNum = 0;
      omtfEvent.omtfProcessor = 10;

      omtfEvent.omtfQuality = 0;
      omtfEvent.killed = false;

      clearOmtfStubs();
      clearOmtfInputStubs();
      
      rootTree->Fill();
    }
  }
  evntCnt++;
}

void DataROOTDumper2::addOmtfInputStubsFromProc(int iProc, l1t::tftype mtfType, AlgoMuonPtr& muon){
  int procIndx = omtfConfig->getProcIndx(iProc, mtfType);
  
  if (!inputInProcs[procIndx]) return; 
  auto& omtfInput = *inputInProcs[procIndx];

  // Get RefHits...
  std::vector<const RefHitDef*> refHitDefs;
  {
    auto refHitsBits = omtfInput.getRefHits(procIndx);
    if (refHitsBits.none())
      return;  // myResults;

    //loop over all possible refHits, e.g. 128
    for (unsigned int iRefHit = 0; iRefHit < omtfConfig->nRefHits(); ++iRefHit) {
      if (!refHitsBits[iRefHit])
        continue;

      refHitDefs.push_back(&(omtfConfig->getRefHitsDefs()[procIndx][iRefHit]));

      if (refHitDefs.size() == omtfConfig->nTestRefHits())
        break;
    }
  }
  
  struct refStub {
    int eta;
    int phi;
    unsigned int iRegion;
    unsigned int iRefLayer;
  };
  std::vector<refStub> refStubs;  
  for (unsigned int iRefHit = 0; iRefHit < refHitDefs.size(); iRefHit++) {
    const RefHitDef& aRefHitDef = *(refHitDefs[iRefHit]);

    unsigned int refLayerLogicNum = omtfConfig->getRefToLogicNumber()[aRefHitDef.iRefLayer];
    const MuonStubPtr refStub = omtfInput.getMuonStub(refLayerLogicNum, aRefHitDef.iInput);
    refStubs.push_back({refStub->etaHw, refStub->phiHw, aRefHitDef.iRegion, aRefHitDef.iRefLayer});
  }
  
  for (unsigned int iLayer = 0; iLayer < omtfConfig->nLayers(); ++iLayer) {
    for (unsigned int iInput = 0; iInput < omtfInput.getMuonStubs()[iLayer].size(); ++iInput) {
      auto layer = iLayer;
      if  (omtfConfig->isBendingLayer(iLayer)) continue; //layer = iLayer - 1;

      auto stub = omtfInput.getMuonStub(layer, iInput);
      if (stub) {  
        omtfEvent.inputStubNo++;
        omtfEvent.inputStubLogicLayer.push_back(stub->logicLayer);
        omtfEvent.inputStubProc.push_back(procIndx);
        omtfEvent.inputStubPhi.push_back(stub->phiHw);
        omtfEvent.inputStubPhiB.push_back(stub->phiBHw);
        omtfEvent.inputStubEta.push_back(stub->etaHw);
        omtfEvent.inputStubQuality.push_back(stub->qualityHw);
        omtfEvent.inputStubBx.push_back(stub->bx);
        omtfEvent.inputStubTiming.push_back(stub->timing);
        omtfEvent.inputStubDetId.push_back(stub->detId);
        omtfEvent.inputStubType.push_back(stub->type);
        omtfEvent.inputStubIsMatched.push_back(isMatchedStub(stub, muon));

        for (auto& refStub : refStubs) {
          int deltaEta = stub->etaHw - refStub.eta;
          int deltaPhi = stub->phiHw - refStub.phi;
          fillStubDeltaEtaPhi(deltaEta, deltaPhi, refStub.iRefLayer);
        }
      }
    }
  }

/*
  for (auto& layer : omtfInput.getMuonStubs()) {
    for (auto& stub : layer) {
	    if (stub) {
        omtfEvent.inputStubNo++;
        omtfEvent.inputStubLogicLayer.push_back(stub->logicLayer);
        omtfEvent.inputStubProc.push_back(procIndx);
        omtfEvent.inputStubPhi.push_back(stub->phiHw);
        omtfEvent.inputStubPhiB.push_back(stub->phiBHw);
        omtfEvent.inputStubEta.push_back(stub->etaHw);
        omtfEvent.inputStubQuality.push_back(stub->qualityHw);
        omtfEvent.inputStubBx.push_back(stub->bx);
        omtfEvent.inputStubTiming.push_back(stub->timing);
        omtfEvent.inputStubDetId.push_back(stub->detId);
        omtfEvent.inputStubType.push_back(stub->type);
        omtfEvent.inputStubIsMatched.push_back(isMatchedStub(stub, muon));

        for (auto& refStub : refStubs) {
          int deltaEta = stub->etaHw - refStub.eta;
          int deltaPhi = stub->phiHw - refStub.phi;
          fillStubDeltaEtaPhi(deltaEta, deltaPhi, refStub.iRefLayer);
        }
      }
    }
  }
  */
}

void DataROOTDumper2::fillStubDeltaEtaPhi(int deltaEta, int deltaPhi, int refLayer) {
  if (refLayer == 0) {
    omtfEvent.inputStubDeltaPhi0.push_back(deltaPhi);
    omtfEvent.inputStubDeltaEta0.push_back(deltaEta);
  } else if (refLayer == 1) {
    omtfEvent.inputStubDeltaPhi1.push_back(deltaPhi);
    omtfEvent.inputStubDeltaEta1.push_back(deltaEta);
  } else if (refLayer == 2) {
    omtfEvent.inputStubDeltaPhi2.push_back(deltaPhi);
    omtfEvent.inputStubDeltaEta2.push_back(deltaEta);
  } else if (refLayer == 3) {
    omtfEvent.inputStubDeltaPhi3.push_back(deltaPhi);
    omtfEvent.inputStubDeltaEta3.push_back(deltaEta);
  } else if (refLayer == 4) {
    omtfEvent.inputStubDeltaPhi4.push_back(deltaPhi);
    omtfEvent.inputStubDeltaEta4.push_back(deltaEta);
  } else if (refLayer == 5) {
    omtfEvent.inputStubDeltaPhi5.push_back(deltaPhi);
    omtfEvent.inputStubDeltaEta5.push_back(deltaEta);
  } else if (refLayer == 6) {
    omtfEvent.inputStubDeltaPhi6.push_back(deltaPhi);
    omtfEvent.inputStubDeltaEta6.push_back(deltaEta);
  } else if (refLayer == 7) {
    omtfEvent.inputStubDeltaPhi7.push_back(deltaPhi);
    omtfEvent.inputStubDeltaEta7.push_back(deltaEta);
  }

}

bool DataROOTDumper2::isMatchedStub(const MuonStubPtr& stub, AlgoMuonPtr& procMuon) {
  if (stub->type == MuonStub::Type::EMPTY)
    return false;

  auto& gpResult = (procMuon->getGpResultUnconstr().getPdfSumUnconstr() > procMuon->getGpResultConstr().getPdfSum())
                    ? procMuon->getGpResultUnconstr() : procMuon->getGpResultConstr();

  for (unsigned int iLogicLayer = 0; iLogicLayer < gpResult.getStubResults().size(); ++iLogicLayer) {
    auto& stubResult = gpResult.getStubResults()[iLogicLayer];   
    if (stubResult.getMuonStub() && stubResult.getMuonStub()->detId == stub->detId) {
      return true;
    }
  }
  return false;
}

bool DataROOTDumper2::isRefLayer(const MuonStubPtr& stub, AlgoMuonPtr& procMuon) {

  if ((int)stub->logicLayer == omtfConfig->getRefToLogicNumber()[procMuon->getRefLayer()])
    return true;

  return false;
}

void DataROOTDumper2::clearOmtfStubs() {
  omtfEvent.stubNo = 0;
  omtfEvent.stubLayer.clear();
  omtfEvent.stubQuality.clear();
  omtfEvent.stubValid.clear();
  omtfEvent.stubZ.clear();
  omtfEvent.stubPhi.clear();
  omtfEvent.stubEta.clear();
  omtfEvent.stubPhiDist.clear();
  omtfEvent.stubEtaDist.clear();
  omtfEvent.stubIsRefLayer.clear();
  omtfEvent.stubTiming.clear();
  omtfEvent.stubDetId.clear();
  omtfEvent.stubBx.clear();
  omtfEvent.stubPhiB.clear();
  omtfEvent.stubR.clear();
  omtfEvent.stubType.clear();
}


void DataROOTDumper2::clearOmtfInputStubs() {
  omtfEvent.inputStubLogicLayer.clear();
  omtfEvent.inputStubProc.clear();
  omtfEvent.inputStubPhi.clear();
  omtfEvent.inputStubPhiB.clear();
  omtfEvent.inputStubEta.clear();
  omtfEvent.inputStubQuality.clear();
  omtfEvent.inputStubBx.clear();
  omtfEvent.inputStubTiming.clear();
  omtfEvent.inputStubDetId.clear();
  omtfEvent.inputStubType.clear();
  omtfEvent.inputStubIsMatched.clear();
  omtfEvent.inputStubDeltaPhi0.clear();
  omtfEvent.inputStubDeltaPhi1.clear();
  omtfEvent.inputStubDeltaPhi2.clear();
  omtfEvent.inputStubDeltaPhi3.clear();
  omtfEvent.inputStubDeltaPhi4.clear();
  omtfEvent.inputStubDeltaPhi5.clear();
  omtfEvent.inputStubDeltaPhi6.clear();
  omtfEvent.inputStubDeltaPhi7.clear();
  omtfEvent.inputStubDeltaEta0.clear();
  omtfEvent.inputStubDeltaEta1.clear();
  omtfEvent.inputStubDeltaEta2.clear();
  omtfEvent.inputStubDeltaEta3.clear();
  omtfEvent.inputStubDeltaEta4.clear();
  omtfEvent.inputStubDeltaEta5.clear();
  omtfEvent.inputStubDeltaEta6.clear();
  omtfEvent.inputStubDeltaEta7.clear();


  omtfEvent.inputStubNo = 0;
}

void DataROOTDumper2::endJob() { edm::LogVerbatim("l1tOmtfEventPrint") << " evntCnt " << evntCnt << endl; }
