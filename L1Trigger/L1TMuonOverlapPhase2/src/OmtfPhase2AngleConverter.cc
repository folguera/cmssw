#include "L1Trigger/L1TMuonOverlapPhase2/interface/OmtfPhase2AngleConverter.h"

namespace {
  int sgn(float val) { return (0 < val) - (val < 0); }

  int etaVal2CodePhase2(float etaVal) {
    int sign = sgn(etaVal);
    int code = (int)round(fabs(etaVal) * 115 / 1.25);
    if (code < 73) return sign * 95; //TODO:  protect the code from being out of range.... 
    return sign * code;
  }
}  // namespace

int OmtfPhase2AngleConverter::getProcessorPhi(int phiZero, l1t::tftype part, int dtScNum, int dtPhi) const {
  constexpr int dtPhiBins = 65536;          //65536. for [-0.5,0.5] radians
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

int OmtfPhase2AngleConverter::getGlobalEta(DTChamberId dTChamberId,
                                           const L1Phase2MuDTThContainer* dtThDigis,
                                           int bxNum, int time) const {
  int dtThBins = 65536;  //65536. for [-6.3,6.3]
  float kconv = 1 / (dtThBins / 2.);

  float eta = -999;
  // get the theta digi
  bool foundeta = false;
  int chi2(999), tdiff(999999), quality(0); 
  for (const auto& thetaDigi : (*(dtThDigis->getContainer()))) {
    // first check we are in the same station/wheel/sector and BX
    if (thetaDigi.whNum() != dTChamberId.wheel() || thetaDigi.stNum() != dTChamberId.station() ||
        thetaDigi.scNum() != (dTChamberId.sector() - 1) || (thetaDigi.bxNum() - 20) == bxNum) 
        continue;
    
    if (quality > thetaDigi.quality() || (quality == thetaDigi.quality() && chi2 > thetaDigi.chi2()) ||
        (quality == thetaDigi.quality() && chi2 == thetaDigi.chi2() && tdiff > abs(thetaDigi.t0()-time))) {
      quality = thetaDigi.quality();
      chi2 = thetaDigi.chi2();
      tdiff = abs(thetaDigi.t0()-time);
 
      // get the theta digi
      float k = thetaDigi.k() * kconv;  //-pow(-1.,z<0)*log(tan(atan(1/k)/2.));
      int sign = sgn(thetaDigi.z());    // sign of the z coordinate   
      eta = -1. * sign * log(fabs(tan(atan(1 / k) / 2.)));

      LogTrace("OMTFReconstruction") << "OmtfPhase2AngleConverter::getGlobalEta(" << dTChamberId << ") eta: " << eta
                                       << " k: " << k << " thetaDigi.k(): " << thetaDigi.k();
      foundeta = true;
    }
  }

  if (foundeta) {
    return abs(etaVal2CodePhase2(eta));
  } else if (dTChamberId.station() == 1){
    return 92;
  } else if (dTChamberId.station() == 2) {
    return 79;
  } else if (dTChamberId.station() == 3) {
    return 75;
  } 
  
  return 0;
}
