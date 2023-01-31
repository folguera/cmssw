#ifndef OmtfPhase2AngleConverter_h
#define OmtfPhase2AngleConverter_h

#include "L1Trigger/L1TMuonOverlapPhase1/interface/Omtf/OmtfAngleConverter.h"
#include "DataFormats/L1DTTrackFinder/interface/L1Phase2MuDTThContainer.h"

class OmtfPhase2AngleConverter : public OmtfAngleConverter {
public:
  OmtfPhase2AngleConverter(){};
  ~OmtfPhase2AngleConverter() override{};

  // Convert DT phi to OMTF coordinate system.
  int getProcessorPhi(int phiZero, l1t::tftype part, int dtScNum, int dtPhi) const override;
  
  //adds the eta segments from the thetaDigi to etaSegments  
  int getGlobalEta(const DTChamberId dTChamberId, const L1Phase2MuDTThContainer *dtThDigis, int bxNum) const;
  
  
};

#endif
