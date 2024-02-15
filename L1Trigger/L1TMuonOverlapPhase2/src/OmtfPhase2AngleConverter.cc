#include "L1Trigger/L1TMuonOverlapPhase2/interface/OmtfPhase2AngleConverter.h"

namespace {
  int sgn(float val) {
    return (0 < val) - (val < 0);
  }

  int etaVal2CodePhase2(float etaVal) {
      int sign = sgn(etaVal);
      int code = fabs(etaVal) * 115 / 1.25;
      LogTrace("l1tOmtfEventPrint") << "OmtfPhase2AngleConverter::etaVal2Code( " << etaVal << " ) --> " << code << std::endl;
      return sign * code;
  }
}

int OmtfPhase2AngleConverter::getProcessorPhi(int phiZero, l1t::tftype part, int dtScNum, int dtPhi) const {
  int dtPhiBins = 65536;                    //65536. for [-0.5,0.5] radians
  double hsPhiPitch = 2 * M_PI / nPhiBins;  // width of phi Pitch, related to halfStrip at CSC station 2

  int sector = dtScNum + 1;  //NOTE: there is a inconsistency in DT sector numb. Thus +1 needed to get detector numb.

  double scale = 0.5 / dtPhiBins / hsPhiPitch;  //was 0.8
  int scale_coeff = lround(scale * (1 << 15));

  int ichamber = sector - 1;
  if (ichamber > 6)
    ichamber = ichamber - 12;

  int offsetGlobal = (int)nPhiBins * ichamber / 12;

  int phiConverted = ((dtPhi * scale_coeff) >> 15) + offsetGlobal - phiZero;

  return config->foldPhi(phiConverted);
}

int OmtfPhase2AngleConverter::getGlobalEta(DTChamberId dTChamberId, const L1Phase2MuDTThContainer *dtThDigis, int bxNum) const{

  //const DTChamberId dTChamberId(aDigi.whNum(),aDigi.stNum(),aDigi.scNum()+1);
  int dtThBins = 65536;  //65536. for [-6.3,6.3]
  float zconv = 1/(dtThBins/1500.); 
  float kconv = 1/(dtThBins/2.);

  float eta = -999;
  // get the theta digi
  for (auto thetaDigi : (*(dtThDigis->getContainer()))) {
    if (thetaDigi.whNum() == dTChamberId.wheel() && thetaDigi.stNum() == dTChamberId.station() &&
        thetaDigi.scNum() == dTChamberId.sector() - 1 && thetaDigi.bxNum() == bxNum) {
      
      // get the theta digi
      float z = thetaDigi.z() * zconv;
      float k = thetaDigi.k() * kconv;
      eta = -pow(-1.,z<0)*log(tan(atan(1/k)/2.));
    }
  }

  int iEta = etaVal2CodePhase2(eta);
  return abs(iEta);
}
