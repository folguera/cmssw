import pickle 
import math 
import ROOT 

pileups = [200]#200]#,300]
aging  = ["","_aging1000","_aging3000"]
qualities = ['_q12'] 
etaHeaders = {"hEta20_q12_cut20":'#splitline{p_{T}^{gen muon} #geq 25 GeV}{p_{T}^{L1 muon} #geq 20 GeV}',"hEta7_15_q12_cut5":'#splitline{7 GeV #leq p_{T}^{gen muon} #leq 15 GeV}{p_{T}^{L1 muon} #geq 5 GeV}'}
outFile = ROOT.TFile("tdr_eff_pt3.root","RECREATE")
outFile.cd()

ROOT.gROOT.ProcessLine('.L PlotTemplate.C+')
ROOT.gROOT.SetBatch(True)
with open('tdr_eff_pt3_PU200.pickle', 'rb') as handle:
    b = pickle.load(handle)

for puValue in pileups:
   for q in qualities:
      
      puHandle = ''
      if puValue == 0: puHandle ='NOPU'
      else: puHandle = 'PU' + str(puValue)
      print puHandle
      for charge in ["5GeV","3GeV","2GeV","1GeV"]:
        for pt in ["3","10","20"]:
            canvas = ROOT.CreateCanvas('name',False,True)
            b['SingleMu_' + puHandle + aging[0]]['eff_pt'+ pt + q + "_" + charge].Draw()
            b['SingleMu_' + puHandle + aging[0]]['eff_pt'+ pt + q + "_" + charge].SetTitle(';Generated muon p_{T} [GeV];Efficiency')
            b['SingleMu_' + puHandle + aging[1]]['eff_pt'+ pt + q + "_" + charge].Draw("same")
            b['SingleMu_' + puHandle + aging[2]]['eff_pt'+ pt + q + "_" + charge].Draw("same")
            b['SingleMu_' + puHandle + aging[0]]['eff_pt'+ pt + q + "_" + charge].SetLineColor(ROOT.kRed)
            b['SingleMu_' + puHandle + aging[1]]['eff_pt'+ pt + q + "_" + charge].SetLineColor(ROOT.kBlue)
            b['SingleMu_' + puHandle + aging[2]]['eff_pt'+ pt + q + "_" + charge].SetLineColor(ROOT.kGreen)
            b['SingleMu_' + puHandle + aging[0]]['eff_pt'+ pt + q + "_" + charge].SetMarkerStyle(8)
            b['SingleMu_' + puHandle + aging[1]]['eff_pt'+ pt + q + "_" + charge].SetMarkerStyle(23)
            b['SingleMu_' + puHandle + aging[2]]['eff_pt'+ pt + q + "_" + charge].SetMarkerStyle(33)
            b['SingleMu_' + puHandle + aging[0]]['eff_pt'+ pt + q + "_" + charge].SetMarkerColor(ROOT.kRed)
            b['SingleMu_' + puHandle + aging[1]]['eff_pt'+ pt + q + "_" + charge].SetMarkerColor(ROOT.kBlue)
            b['SingleMu_' + puHandle + aging[2]]['eff_pt'+ pt + q + "_" + charge].SetMarkerColor(ROOT.kGreen)
            b['SingleMu_' + puHandle + aging[0]]['eff_pt'+ pt + q + "_" + charge].SetMarkerSize(1.2)
            b['SingleMu_' + puHandle + aging[1]]['eff_pt'+ pt + q + "_" + charge].SetMarkerSize(1.5)
            b['SingleMu_' + puHandle + aging[2]]['eff_pt'+ pt + q + "_" + charge].SetMarkerSize(1.5)
            b['SingleMu_' + puHandle + aging[0]]['eff_pt'+ pt + q + "_" + charge].SetLineWidth(2)
            b['SingleMu_' + puHandle + aging[1]]['eff_pt'+ pt + q + "_" + charge].SetLineWidth(2)
            b['SingleMu_' + puHandle + aging[2]]['eff_pt'+ pt + q + "_" + charge].SetLineWidth(2)
            canvas.Update()
            g0 = b['SingleMu_' + puHandle + aging[0]]['eff_pt'+ pt + q + "_" + charge].GetPaintedHistogram()
            g1 = b['SingleMu_' + puHandle + aging[1]]['eff_pt'+ pt + q + "_" + charge].GetPaintedHistogram()
            g2 = b['SingleMu_' + puHandle + aging[2]]['eff_pt'+ pt + q + "_" + charge].GetPaintedHistogram()

      
            leg = ROOT.TLegend(0.5,0.60,0.85,0.15);
            leg.SetTextSize(0.035);
            leg.SetHeader("p_{T}^{L1 muon} #geq " + pt + " GeV")
            leg.AddEntry(b['SingleMu_' + puHandle + aging[0]]['eff_pt'+ pt + q + "_" + charge],"No Aging ",'l');
            leg.AddEntry(b['SingleMu_' + puHandle + aging[1]]['eff_pt'+ pt + q + "_" + charge],"1000 fb^{-1} aging",'l')
            leg.AddEntry(b['SingleMu_' + puHandle + aging[2]]['eff_pt'+ pt + q + "_" + charge],"3000 fb^{-1} aging",'l')
      
            ROOT.DrawPrelimLabel(canvas)
            ROOT.DrawLumiLabel(canvas,'%i PU'%puValue)
            leg.Draw("same")

            ROOT.SaveCanvas(canvas,'tdr_pt_eff'+ q + "_pt" + str(pt)+ "_" + charge + puHandle)


      for charge in [""]:
        for eta in ["hEta20_q12_cut20","hEta7_15_q12_cut5"]:
            canvas = ROOT.CreateCanvas('name',False,True)
            b['SingleMu_' + puHandle + aging[0]][eta].Draw()
            b['SingleMu_' + puHandle + aging[0]][eta].SetTitle(';Generated muon #eta ;Efficiency')
            b['SingleMu_' + puHandle + aging[1]][eta].Draw("same")
            b['SingleMu_' + puHandle + aging[2]][eta].Draw("same")
            b['SingleMu_' + puHandle + aging[0]][eta].SetLineColor(ROOT.kRed)
            b['SingleMu_' + puHandle + aging[1]][eta].SetLineColor(ROOT.kBlue)
            b['SingleMu_' + puHandle + aging[2]][eta].SetLineColor(ROOT.kGreen)
            b['SingleMu_' + puHandle + aging[0]][eta].SetMarkerStyle(8)
            b['SingleMu_' + puHandle + aging[1]][eta].SetMarkerStyle(23)
            b['SingleMu_' + puHandle + aging[2]][eta].SetMarkerStyle(33)
            b['SingleMu_' + puHandle + aging[0]][eta].SetMarkerColor(ROOT.kRed)
            b['SingleMu_' + puHandle + aging[1]][eta].SetMarkerColor(ROOT.kBlue)
            b['SingleMu_' + puHandle + aging[2]][eta].SetMarkerColor(ROOT.kGreen)
            b['SingleMu_' + puHandle + aging[0]][eta].SetMarkerSize(1.2)
            b['SingleMu_' + puHandle + aging[1]][eta].SetMarkerSize(1.5)
            b['SingleMu_' + puHandle + aging[2]][eta].SetMarkerSize(1.5)
            b['SingleMu_' + puHandle + aging[0]][eta].SetLineWidth(2)
            b['SingleMu_' + puHandle + aging[1]][eta].SetLineWidth(2)
            b['SingleMu_' + puHandle + aging[2]][eta].SetLineWidth(2)
            l1 = ROOT.TLine(0.82,0,0.82,1)
            l2 = ROOT.TLine(-0.82,0,-0.82,1)
            l3 = ROOT.TLine(1.23,0,1.23,1)
            l4 = ROOT.TLine(-1.23,0,-1.23,1)
            l1.SetLineWidth(2)
            l1.SetLineStyle(10)
            l1.SetLineColor(ROOT.kBlack)
      
            l2.SetLineWidth(2)
            l2.SetLineStyle(10)
            l2.SetLineColor(ROOT.kBlack)
      
            l3.SetLineWidth(2)
            l3.SetLineStyle(10)
            l3.SetLineColor(ROOT.kBlack)
      
            l4.SetLineWidth(2)
            l4.SetLineStyle(10)
            l4.SetLineColor(ROOT.kBlack)
            l1.Draw()
            l2.Draw()
            l3.Draw()
            l4.Draw()
      
            leg = ROOT.TLegend(0.50,0.7,0.9,0.25);
            leg.SetTextSize(0.035);
            leg.SetHeader(etaHeaders[eta])
            leg.AddEntry(b['SingleMu_' + puHandle + aging[0]][eta],"No Aging ",'l');
            leg.AddEntry(b['SingleMu_' + puHandle + aging[1]][eta],"1000 fb^{-1} aging",'l')
            leg.AddEntry(b['SingleMu_' + puHandle + aging[2]][eta],"3000 fb^{-1} aging",'l')

            ROOT.DrawPrelimLabel(canvas)
            ROOT.DrawLumiLabel(canvas,'%i PU'%puValue)
            leg.Draw("same")

            ROOT.SaveCanvas(canvas,'tdr_%s_eff'%eta+ "_PU"+str(puValue))

outFile.Close()
