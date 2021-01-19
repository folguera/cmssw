/*
 * PdfModuleWithStats.h
 *
 *  Created on: Feb 4, 2019
 *      Author: Karol Bunkowski kbunkow@cern.ch
 */

#ifndef INTERFACE_PDFMODULEWITHSTATS_H_
#define INTERFACE_PDFMODULEWITHSTATS_H_

#include "L1Trigger/L1TkMuonBayes/interface/PdfModule.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "TH2I.h"

class PdfModuleWithStats : public PdfModule {
public:
  PdfModuleWithStats(MuCorrelatorConfigPtr& config);

  ~PdfModuleWithStats() override;

  float getPdfVal(
      unsigned int layer, unsigned int etaBin, unsigned int refLayer, unsigned int ptBin, int pdfBin) override;

  //writes pdfHists to current root file
  //virtual void write() const;

  virtual void generateCoefficients();

  virtual void generateCoefficients1();

private:
  //[layer][etaBin][refLayer](ptBin, pdfBin)
  std::vector<std::vector<std::vector<TH2I*> > > pdfHists;

  edm::Service<TFileService> fs;

  double sigmaFactor = 1.;
};

#endif /* INTERFACE_PDFMODULEWITHSTATS_H_ */
