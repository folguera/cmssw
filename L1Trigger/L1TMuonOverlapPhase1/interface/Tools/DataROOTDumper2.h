/*
 * DataROOTDumper2.h
 *
 *  Created on: Dec 11, 2019
 *      Author: kbunkow
 */

#ifndef L1T_OmtfP1_TOOLS_DATAROOTDUMPER2_H_
#define L1T_OmtfP1_TOOLS_DATAROOTDUMPER2_H_

#include "L1Trigger/L1TMuonOverlapPhase1/interface/Tools/EmulationObserverBase.h"
#include "L1Trigger/L1TMuonOverlapPhase1/interface/Tools/CandidateSimMuonMatcher.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "SimDataFormats/Track/interface/SimTrackContainer.h"

#include "TMap.h"
#include "TArrayI.h"
#include "TFile.h"
#include "TH2.h"

#include <functional>

class TTree;

struct OmtfEvent {
public:
  unsigned int eventNum = 0;

  //muonPt = 0 means that no muon was matched to the candidate
  short muonEvent = -1;
  float muonPt = 0, muonEta = 0, muonPhi = 0, muonPropEta = 0, muonPropPhi = 0;
  char muonCharge = 0;
  float muonDxy = 0;
  float muonRho = 0;

  float omtfPt = 0, omtfEta = 0, omtfPhi = 0, omtfUPt = 0;
  char omtfCharge = 0;
  char omtfProcessor = 0;
  short omtfScore = 0;

  short omtfHwEta = 0;

  char omtfQuality = 0;
  char omtfRefLayer = 0;
  char omtfRefHitNum = 0;

  unsigned int omtfFiredLayers = 0;

  bool killed = false;

  float deltaPhi = 0, deltaEta = 0;

  //float omtfPtCont = 0;
  int stubNo = 0;
  std::vector<unsigned int> stubLayer;
  std::vector<unsigned int> stubQuality;
  std::vector<int> stubZ, stubValid, stubEta, stubPhi,stubPhiB, stubR, stubPhiDist,stubEtaDist;
  std::vector<bool> stubIsRefLayer;
  std::vector<int> stubBx, stubTiming;
  std::vector<int> stubDetId;
  std::vector<int> stubType;
  
  // INPUT stubs 
  int inputStubNo = 0;
  std::vector<unsigned int> inputStubLogicLayer;
  std::vector<int> inputStubProc;
  std::vector<int> inputStubPhi;
  std::vector<int> inputStubPhiB;
  std::vector<int> inputStubEta;
  std::vector<unsigned int> inputStubQuality;
  std::vector<int> inputStubBx;
  std::vector<int> inputStubTiming;
  std::vector<int> inputStubDetId;
  std::vector<int> inputStubType;
  std::vector<bool> inputStubIsMatched; 

  std::vector<int> inputStubDeltaPhi0;
  std::vector<int> inputStubDeltaPhi1;
  std::vector<int> inputStubDeltaPhi2;
  std::vector<int> inputStubDeltaPhi3;
  std::vector<int> inputStubDeltaPhi4;
  std::vector<int> inputStubDeltaPhi5;
  std::vector<int> inputStubDeltaPhi6;
  std::vector<int> inputStubDeltaPhi7;
  std::vector<int> inputStubDeltaEta0;
  std::vector<int> inputStubDeltaEta1;
  std::vector<int> inputStubDeltaEta2;
  std::vector<int> inputStubDeltaEta3;
  std::vector<int> inputStubDeltaEta4;
  std::vector<int> inputStubDeltaEta5;
  std::vector<int> inputStubDeltaEta6;
  std::vector<int> inputStubDeltaEta7;


  /* DEACTIVATE HIT Structure... 
    struct Hit {
      union {
      unsigned long rawData = 0;
      struct {
        char layer;
        char quality;
        char z;
        char valid;
        short eta;
        short phiDist;
      };
    };
    ~Hit() {}
  };
  std::vector<unsigned long> hits;
  */
};

class DataROOTDumper2 : public EmulationObserverBase {
public:
  DataROOTDumper2(const edm::ParameterSet& edmCfg,
                  const OMTFConfiguration* omtfConfig,
                  CandidateSimMuonMatcher* candidateSimMuonMatcher);

  ~DataROOTDumper2() override;

  void observeProcesorEmulation(unsigned int iProcessor,
                                l1t::tftype mtfType,
                                const std::shared_ptr<OMTFinput>&,
                                const AlgoMuons& algoCandidates,
                                const AlgoMuons& gbCandidates,
                                const std::vector<l1t::RegionalMuonCand>& candMuons) override;
  void observeEventBegin(const edm::Event& iEvent) override;
  void observeEventEnd(const edm::Event& iEvent,
                       std::unique_ptr<l1t::RegionalMuonCandBxCollection>& finalCandidates) override;

  void addOmtfInputStubsFromProc(int iProc, l1t::tftype mtfType) {};
  void addOmtfInputStubsFromProc(int iProc, l1t::tftype mtfType, AlgoMuonPtr& procMuon);
  bool isMatchedStub(const MuonStubPtr& stub, AlgoMuonPtr& procMuon);
  bool isRefLayer(const MuonStubPtr& stub, AlgoMuonPtr& procMuon);
  void addOmtfRestrictedStubsFromProc(int iProc, l1t::tftype mtfType, int refLayer) {};
  void fillStubDeltaEtaPhi(int deltaEta, int deltaPhi, int refLayer);
  void clearOmtfStubs();
  void clearOmtfInputStubs();
  void endJob() override;

private:
  void initializeTTree();

  CandidateSimMuonMatcher* candidateSimMuonMatcher = nullptr;

  TTree* rootTree = nullptr;

  OmtfEvent omtfEvent;
  std::vector<std::shared_ptr<OMTFinput> > inputInProcs;

  unsigned int evntCnt = 0;

  TH1I* ptGenPos = nullptr;
  TH1I* ptGenNeg = nullptr;

  std::vector<TH2*> hitVsPt;

  bool dumpKilledOmtfCands = false;

  bool usePropagation = false;
};

#endif /* L1T_OmtfP1_TOOLS_DATAROOTDUMPER2_H_ */
