import pickle, os
import math 
import ROOT 

pileups = [200]
#ss = ["Nu_PU200_aged3000","Nu_PU200_aged1000","Nu_PU200"]
ss = ["Nu_PU200"]
#samples = {"Nu_PU200_aged3000":ROOT.kBlue,"Nu_PU200_aged1000":ROOT.kRed,"Nu_PU200":ROOT.kBlack}
samples = {"Nu_PU200":ROOT.kBlack}
#tags = {"Nu_PU200_aged1000":"1000 fb^{-1} Aging","Nu_PU200_aged3000":"3000 fb^{-1} Aging","Nu_PU200":"No Aging"}
tags = {"Nu_PU200":"No Aging"}
qualities = ['_q12'] 
ROOT.gROOT.SetBatch(True)

ROOT.gROOT.ProcessLine('.L PlotTemplate.C+')

with open('tdr_rates_aged_all.pickle', 'rb') as handle:
    bb = pickle.load(handle)

outpath = "/afs/cern.ch/user/f/folguera/www/private/L1TPhase2/OMTF/2001_AdaptingToP2TPs/P1TPs/"

if not os.path.exists(outpath):
    os.mkdir(outpath)
    print "cp ~folguera/public/utils/index.php %s/" %outpath
    os.system("cp ~folguera/public/utils/index.php %s/" %outpath)

outFile = ROOT.TFile("tdr_rates.root","RECREATE")
outFile.cd()

bins = [0.,1.,2.,3.,4.,4.5,5.,6.,7.,8.,10.,12.,14.,16.,18.,20.,25.,30.,35.,40.,45.,50.,60.,70.,80.,90.,100.,120.,140.,200.,250.]
cbins = []
for i in range(len(bins)-1):
    cbins.append((bins[i] + bins[i+1])/2.)


coeff = 2760*11.246 

hp = ROOT.TH1F('hp','',1,-0.5,0.5)
ht = ROOT.TH1F('ht','',1,-0.5,0.5)

for puValue in pileups:
 gr = {}
 canvas = ROOT.CreateCanvas('name',True,True)
 leg = ROOT.TLegend(0.55,0.65,0.9,0.48)
 drawn = False
 for s in ss:
   for q in qualities:
      puHandle = ''
      if puValue == 0: puHandle ='NOPU'
      else: puHandle = 'PU' + str(puValue)
      gr[s]      = ROOT.TGraphAsymmErrors(len(bins)-1)
      for i, b in enumerate(cbins):
          hp.SetBinContent(1, bb[s]['fired'+str(bins[i])+ q] )
          ht.SetBinContent(1, bb[s]['total'] ) 
          eff = ROOT.TEfficiency(hp, ht)
          val    = coeff * eff.GetEfficiency(1)
          val_up = coeff * eff.GetEfficiencyErrorUp(1)
          val_dn = coeff * eff.GetEfficiencyErrorLow(1)

          gr[s].SetPoint(i, b, val)
          gr[s].SetPointEYlow(i, val_dn)
          gr[s].SetPointEYhigh(i, val_up)
          gr[s].SetPointEXlow(i, b - bins[i])
          gr[s].SetPointEXhigh(i, bins[i+1] - b)
          print s, b, val
      #Set drawing options and draw the gr[s]aph
      #canvas.SetLogx(True)
      gr[s].SetMarkerColor(samples[s])
      gr[s].SetLineColor(samples[s])
      gr[s].GetXaxis().SetLimits(0,100)
      gr[s].GetXaxis().SetTitle("L1 p_{T}^{cut} [GeV]")
      gr[s].GetYaxis().SetTitle("Rate [kHz]")
      gr[s].SetTitle("")
      if not(drawn):
        gr[s].Draw("AP")
        drawn = True
      else:
        gr[s].Draw("P same")
      leg.AddEntry(gr[s],tags[s],'l')
 leg.Draw("same")
 ROOT.DrawPrelimLabel(canvas)
 ROOT.DrawLumiLabel(canvas,'14 TeV, %i PU'%puValue)
 ROOT.SaveCanvas(canvas, outpath + 'tdr_pt_rate'+ q + '_PU_log' + str(puValue))

outFile.Close()
