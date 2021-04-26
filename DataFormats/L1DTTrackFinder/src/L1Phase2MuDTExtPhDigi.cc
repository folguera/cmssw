//-------------------------------------------------
//
//   Class L1MuDTChambPhDigi
//
//   Description: trigger primtive data for the
//                muon barrel Phase2 trigger
//
//
//   Author List: Federica Primavera  Bologna INFN
//
//
//--------------------------------------------------

//-----------------------
// This Class's Header --
//-----------------------
#include "DataFormats/L1DTTrackFinder/interface/L1Phase2MuDTExtPhDigi.h"

//-------------------------------
// Collaborating Class Headers --
//-------------------------------

//---------------
// C++ Headers --
//---------------

//-------------------
// Initializations --
//-------------------

//----------------
// Constructors --
//----------------
L1Phase2MuDTExtPhDigi::L1Phase2MuDTExtPhDigi():

  L1Phase2MuDTPhDigi(),

  m_xLocal(0),
  m_tanPsi(0) {
  
  for (int i=0; i<8; i++) {
    m_pathWireId[i] = -1;
    m_pathTDC[i] = -1;
    m_pathLat[i] = 2;
  }
}

L1Phase2MuDTExtPhDigi::L1Phase2MuDTExtPhDigi(int bx, int wh, int sc, int st, int sl, int phi, int phib, int qual, int idx, int t0, int chi2, int x, int tan, int rpc, int wireId[8], int tdc[8],int lat[8]): 
  
  L1Phase2MuDTPhDigi(bx, wh, sc, st, sl, phi, phib, qual, idx, t0, chi2, rpc),
  m_xLocal(x),
  m_tanPsi(tan) 
{
  for (int i=0; i<8; i++) {
    m_pathWireId[i] = wireId[i];
    m_pathTDC[i] = tdc[i];
    m_pathLat[i] = lat[i];
  }
}

int L1Phase2MuDTExtPhDigi::pathWireId(int i) const { return m_pathWireId[i]; }

int L1Phase2MuDTExtPhDigi::pathTDC(int i) const { return m_pathTDC[i]; }

int L1Phase2MuDTExtPhDigi::pathLat(int i) const { return m_pathLat[i]; }
