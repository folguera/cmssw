#include "L1Trigger/L1TMuonOverlapPhase2/interface/OmtfPhase2AngleConverter.h"

int OmtfPhase2AngleConverter::getProcessorPhi(int phiZero, l1t::tftype part, int dtScNum, int dtPhi) const {
  int dtPhiBins = 65536;                    //65536. for [-0.5,0.5] radians
  double hsPhiPitch = 2 * M_PI / nPhiBins;  // width of phi Pitch, related to halfStrip at CSC station 2

  int sector = dtScNum + 1;  //NOTE: there is a inconsistency in DT sector numb. Thus +1 needed to get detector numb.

  double scale = 0.5 / dtPhiBins / hsPhiPitch;  //was 0.8
  int scale_coeff = lround(scale * pow(2, 11));

  int ichamber = sector - 1;
  if (ichamber > 6)
    ichamber = ichamber - 12;

  int offsetGlobal = (int)nPhiBins * ichamber / 12;

  int phiConverted = floor(dtPhi * scale_coeff / pow(2, 11)) + offsetGlobal - phiZero;

  return config->foldPhi(phiConverted);
}

int getGlobalEta(const DTChamberId dTChamberId, const L1Phase2MuDTThContainer *dtThDigis, int bxNum) const {

  //const DTChamberId dTChamberId(aDigi.whNum(),aDigi.stNum(),aDigi.scNum()+1);
  DTTrigGeom trig_geom(_geodt->chamber(dTChamberId), false);

  /* debug printout to check the geometry of the chambers
  Local2DPoint chamberMiddleLP(0, 0);
  GlobalPoint chamberMiddleGP = _geodt->chamber(dTChamberId)->toGlobal(chamberMiddleLP);
  float phin = (dTChamberId.sector()-1)*Geom::pi()/6;
  float phiRF = _geodt->chamber(dTChamberId)->position().phi();
  float deltaPhi = phiRF - phin;

  LogTrace("l1tOmtfEventPrint")<<"OmtfAngleConverter::getGlobalEta "<<dTChamberId
    <<" perp "<<chamberMiddleGP.perp()
    //<<" chamber()->position().perp() "<<_geodt->chamber(dTChamberId)->position().perp()
    <<" x "<<_geodt->chamber(dTChamberId)->position().x()
    <<" y "<<_geodt->chamber(dTChamberId)->position().y()
    <<" z "<<_geodt->chamber(dTChamberId)->position().z()
    <<" - phiRF "<<phiRF << " rad "<< phiRF * 180. / M_PI<<" deg "
    <<" - phin "<<phin<< " rad "<< phin * 180. / M_PI<<" deg "
    <<" - deltaPhi "<<deltaPhi<<" r "<<chamberMiddleGP.perp() * cos(deltaPhi);
    //<<" distSL "<<trig_geom.distSL();
  */

  // super layer one is the theta superlayer in a DT chamber
  // station 4 does not have a theta super layer
  // the BTI index from the theta trigger is an OR of some BTI outputs
  // so, we choose the BTI that's in the middle of the group
  // as the BTI that we get theta from
  // TODO:::::>>> need to make sure this ordering doesn't flip under wheel sign
  const int NBTI_theta = ((dTChamberId.station() != 4) ? trig_geom.nCell(2) : trig_geom.nCell(3));

  const L1MuDTChambThDigi *theta_segm =
      dtThDigis->chThetaSegm(dTChamberId.wheel(), dTChamberId.station(), dTChamberId.sector() - 1, bxNum);

  int bti_group = -1;
  if (theta_segm) {
    for (unsigned int i = 0; i < 7; ++i)
      if (theta_segm->position(i) && bti_group < 0)
        bti_group = i;
      else if (theta_segm->position(i) && bti_group > -1)
        bti_group = 511;
  }

  int iEta = 0;
  if (bti_group == 511)
    iEta = 95;
  else if (bti_group == -1 && dTChamberId.station() == 1)
    iEta = 92;
  else if (bti_group == -1 && dTChamberId.station() == 2)
    iEta = 79;
  else if (bti_group == -1 && dTChamberId.station() == 3)
    iEta = 75;
  else if (dTChamberId.station() != 4 && bti_group >= 0) {
    unsigned bti_actual = bti_group * NBTI_theta / 7 + NBTI_theta / 14 + 1;
    DTBtiId thetaBTI = DTBtiId(dTChamberId, 2, bti_actual);
    GlobalPoint theta_gp = trig_geom.CMSPosition(thetaBTI);
    iEta = etaVal2Code(fabs(theta_gp.eta()));
  }
  int signEta = sgn(dTChamberId.wheel());
  iEta *= signEta;
  return iEta;  
}
