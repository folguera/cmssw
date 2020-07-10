/*
 * InputMakerPhase2.cpp
 *
 *  Created on: May 20, 2020
 *      Author: kbunkow
 */

#include "FWCore/MessageLogger/interface/MessageLogger.h"
#include "DataFormats/MuonDetId/interface/DTChamberId.h"
#include "L1Trigger/L1TMuonOverlapPhase2/interface/InputMakerPhase2.h"
#include <iostream>

/////////////////////////////////////
void DtPhase2DigiToStubsConverter::loadDigis(const edm::Event& event) {
  event.getByToken(inputTokenDtPh, dtPhDigis);
  event.getByToken(inputTokenDtTh, dtThDigis);
}

void DtPhase2DigiToStubsConverter::makeStubs(
    MuonStubPtrs2D& muonStubsInLayers, unsigned int iProcessor, l1t::tftype procTyp, int bxFrom, int bxTo) {
  if (!dtPhDigis)
    return;

  for (const auto& digiIt : *dtPhDigis->getContainer()) {
    DTChamberId detid(digiIt.whNum(), digiIt.stNum(), digiIt.scNum() + 1);

    ///Check it the data fits into given processor input range
    if (!acceptDigi(detid, iProcessor, procTyp))
      continue;
    
    // HACK for Phase-2  (DT TPs are centered in bX=20)
    if (digiIt.bxNum()-20 >= bxFrom && digiIt.bxNum()-20 <= bxTo) 
      addDTphiDigi(muonStubsInLayers, digiIt, dtThDigis.product(), iProcessor, procTyp);
  }

  if (!mergePhiAndTheta) {
    for (auto& thetaDigi : (*(dtThDigis->getContainer()))) {
      if (thetaDigi.bxNum() >= bxFrom && thetaDigi.bxNum() <= bxTo) {
        addDTetaStubs(muonStubsInLayers, thetaDigi, iProcessor, procTyp);
      }
    }
  }
}
//dtThDigis is provided as argument, because in the OMTF implementation the phi and eta digis are merged (even thought it is artificial)
void DtPhase2DigiToStubsConverterOmtf::addDTphiDigi(MuonStubPtrs2D& muonStubsInLayers,
                                                    const L1Phase2MuDTPhDigi& digi,
                                                    const L1MuDTChambThContainer* dtThDigis,
                                                    unsigned int iProcessor,
                                                    l1t::tftype procTyp) {
  DTChamberId detid(digi.whNum(), digi.stNum(), digi.scNum() + 1);

  if (digi.quality() == 7 || digi.quality() < config->getMinDtPhiQuality())
    return;

  unsigned int hwNumber = config->getLayerNumber(detid.rawId());
  if (config->getHwToLogicLayer().find(hwNumber) == config->getHwToLogicLayer().end())
    return;

  auto iter = config->getHwToLogicLayer().find(hwNumber);
  unsigned int iLayer = iter->second;
  unsigned int iInput = OMTFinputMaker::getInputNumber(config, detid.rawId(), iProcessor, procTyp);
  MuonStub stub;

  stub.type = MuonStub::DT_PHI_ETA;
  stub.phiHw = angleConverter->getProcessorPhi(
      OMTFinputMaker::getProcessorPhiZero(config, iProcessor), procTyp, digi.scNum(), digi.phi());
  stub.etaHw = angleConverter->getGlobalEta(detid, dtThDigis, digi.bxNum()-20);
  //phiB in Ph2 has 2018==1.4rad ... need to convert them to 512==1rad (so we can use OLD patterns)
  stub.phiBHw = digi.phiBend(); //(int)(digi.phiBend()*1.4*512/2048); 
  stub.qualityHw = digi.quality();

  // need to shift 20-BX to roll-back the shift introduced by the DT TPs
  stub.bx = digi.bxNum()-20;
  stub.logicLayer = iLayer;
  stub.detId = detid;

  OMTFinputMaker::addStub(config, muonStubsInLayers, iLayer, iInput, stub);
}

void DtPhase2DigiToStubsConverterOmtf::addDTetaStubs(MuonStubPtrs2D& muonStubsInLayers,
                                                     const L1MuDTChambThDigi& thetaDigi,
                                                     unsigned int iProcessor,
                                                     l1t::tftype procTyp) {
  //in the Phase1 omtf the theta stubs are merged with the phi in the addDTphiDigi
  //TODO implement if needed
}

bool DtPhase2DigiToStubsConverterOmtf::acceptDigi(const DTChamberId& dTChamberId,
                                                  unsigned int iProcessor,
                                                  l1t::tftype procType) {
  return OMTFinputMaker::acceptDtDigi(config, dTChamberId, iProcessor, procType);
}

InputMakerPhase2::InputMakerPhase2(const edm::ParameterSet& edmParameterSet,
                                   MuStubsInputTokens& muStubsInputTokens,
                                   edm::EDGetTokenT<L1Phase2MuDTPhContainer> inputTokenDTPhPhase2,
                                   const OMTFConfiguration* config)
    : OMTFinputMaker(edmParameterSet, muStubsInputTokens, config) {
  edm::LogImportant("OMTFReconstruction") << "constructing InputMakerPhase2" << std::endl;
  
  angleConverter = std::make_unique<OmtfPhase2AngleConverter>(); 
  if (edmParameterSet.getParameter<bool>("usePhase2DTPrimitives")) {
    if (edmParameterSet.getParameter<bool>("dropDTPrimitives") != true)
      throw cms::Exception(
          "L1TMuonOverlapPhase2 InputMakerPhase2::InputMakerPhase2 usePhase2DTPrimitives is true, but dropDTPrimitives "
          "is not true");
    //if the Phase2DTPrimitives are used, then the phase1 DT primitives should be dropped
    digiToStubsConverters.emplace_back(std::make_unique<DtPhase2DigiToStubsConverterOmtf>(
											  config, angleConverter.get(), inputTokenDTPhPhase2, muStubsInputTokens.inputTokenDtTh));
  }
}

InputMakerPhase2::~InputMakerPhase2() {
  // TODO Auto-generated destructor stub
}
