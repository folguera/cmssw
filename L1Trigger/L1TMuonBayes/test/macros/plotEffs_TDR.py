import pickle 
import math 
import ROOT 

pileups = [200,]#200]#,300]
aging  = [""]
qualities = ['_q12'] 

outFile = ROOT.TFile("tdr_eff_moreetabins_PU200.root","RECREATE")
outFile.cd()

ROOT.gROOT.ProcessLine('.L PlotTemplate.C+')
ROOT.gROOT.SetBatch(True)
with open('tdr_eff_moreetabins_PU200.pickle', 'rb') as handle:
    b = pickle.load(handle)

for puValue in pileups:
  for agingValue in aging:
   for q in qualities:
      canvas = ROOT.CreateCanvas('name',False,True)
      puHandle = ''
      if puValue == 0: puHandle ='NOPU'
      else: puHandle = 'PU' + str(puValue)
      puHandle += agingValue
      print puHandle
      for charge in ["5GeV","3GeV","2GeV","1GeV"]:
            b['SingleMu_' + puHandle]['eff_pt3' + q + "_" + charge].SetName('eff_pt3' + q + "_" + charge + puHandle)
            b['SingleMu_' + puHandle]['eff_pt10'+ q + "_" + charge].SetName('eff_pt10' + q + "_" + charge + puHandle)
            b['SingleMu_' + puHandle]['eff_pt20'+ q + "_" + charge].SetName('eff_pt20' + q + "_" + charge + puHandle)

            b['SingleMu_' + puHandle]['eff_pt3' + q + "_" + charge].Write()
            b['SingleMu_' + puHandle]['eff_pt10'+ q + "_" + charge].Write()
            b['SingleMu_' + puHandle]['eff_pt20'+ q + "_" + charge].Write()
            b['SingleMu_' + puHandle]['eff_pt3'+ q + "_" + charge].Draw()
            b['SingleMu_' + puHandle]['eff_pt3'+ q + "_" + charge].SetTitle(';Generated muon p_{T} [GeV];Efficiency')
            b['SingleMu_' + puHandle]['eff_pt10'+ q+ "_" + charge].Draw("same")
            b['SingleMu_' + puHandle]['eff_pt20'+ q+ "_" + charge].Draw("same")
            b['SingleMu_' + puHandle]['eff_pt3'+ q + "_" + charge].SetLineColor(ROOT.kRed)
            b['SingleMu_' + puHandle]['eff_pt10'+ q+ "_" + charge].SetLineColor(ROOT.kBlue)
            b['SingleMu_' + puHandle]['eff_pt20'+ q+ "_" + charge].SetLineColor(ROOT.kGreen)
            b['SingleMu_' + puHandle]['eff_pt3'+ q + "_" + charge].SetMarkerStyle(8)
            b['SingleMu_' + puHandle]['eff_pt10'+ q+ "_" + charge].SetMarkerStyle(23)
            b['SingleMu_' + puHandle]['eff_pt20'+ q+ "_" + charge].SetMarkerStyle(33)
            b['SingleMu_' + puHandle]['eff_pt3'+ q + "_" + charge].SetMarkerColor(ROOT.kRed)
            b['SingleMu_' + puHandle]['eff_pt10'+ q+ "_" + charge].SetMarkerColor(ROOT.kBlue)
            b['SingleMu_' + puHandle]['eff_pt20'+ q+ "_" + charge].SetMarkerColor(ROOT.kGreen)

            b['SingleMu_' + puHandle]['eff_pt3'+ q + "_" + charge].SetMarkerSize(1.2)
            b['SingleMu_' + puHandle]['eff_pt10'+ q+ "_" + charge].SetMarkerSize(1.5)
            b['SingleMu_' + puHandle]['eff_pt20'+ q+ "_" + charge].SetMarkerSize(1.5)


            b['SingleMu_' + puHandle]['eff_pt3'+ q + "_" + charge].SetLineWidth(2)
            b['SingleMu_' + puHandle]['eff_pt10'+ q+ "_" + charge].SetLineWidth(2)
            b['SingleMu_' + puHandle]['eff_pt20'+ q+ "_" + charge].SetLineWidth(2)
      
      
            leg = ROOT.TLegend(0.5,0.6,0.85,0.26);
            leg.SetTextSize(0.035);
            leg.AddEntry(b['SingleMu_' + puHandle]['eff_pt3'+ q+ "_" + charge],'p_{T}^{L1 muon} #geq 3 GeV','l');
            leg.AddEntry(b['SingleMu_' + puHandle]['eff_pt10'+ q+ "_" + charge],'p_{T}^{L1 muon} #geq 10 GeV','l');
            leg.AddEntry(b['SingleMu_' + puHandle]['eff_pt20'+ q+ "_" + charge],'p_{T}^{L1 muon} #geq 20 GeV','l');
      
            ROOT.DrawPrelimLabel(canvas)
            ROOT.DrawLumiLabel(canvas,'%i PU'%puValue)
            leg.Draw("same")

            ROOT.SaveCanvas(canvas,'tdr_pt_eff'+ q + str(puHandle)+ "_" + charge)

      canvas2 = ROOT.CreateCanvas('name2',False,True)
      canvas2.cd()
      b['SingleMu_' + puHandle]['hEta20_q12_cut20'].SetName("hEta20_q12_cut20" + puHandle)
      b['SingleMu_' + puHandle]['hEta20_q12_cut20'].Write()
      b['SingleMu_' + puHandle]['hEta20_q12_cut20'].Draw()
      canvas2.Update()
      graph = b['SingleMu_' + puHandle]['hEta20_q12_cut20'].GetPaintedGraph()
      graph.GetXaxis().SetRangeUser(0.,2.4)
      #graph.GetXaxis().SetMaximum(2.)
      #canvas2.Update()
      #graph = b['SingleMu_' + puHandle]['hEta20_q12_cut20'].GetPaintedGraph()
      #graph.SetMinimum(0.6)
      #graph.SetMaximum(1.01)
      b['SingleMu_' + puHandle]['hEta20_q12_cut20'].SetTitle(';Generated muon  #eta;Efficiency')
      l1 = ROOT.TLine(0.82,0,0.82,1)
      l2 = ROOT.TLine(-0.82,0,-0.82,1)
      l3 = ROOT.TLine(1.23,0,1.23,1)
      l4 = ROOT.TLine(-1.23,0,-1.23,1)
      l1.SetLineWidth(2)
      l1.SetLineStyle(10)
      l1.SetLineColor(ROOT.kRed)

      l2.SetLineWidth(2)
      l2.SetLineStyle(10)
      l2.SetLineColor(ROOT.kRed)

      l3.SetLineWidth(2)
      l3.SetLineStyle(10)
      l3.SetLineColor(ROOT.kRed)

      l4.SetLineWidth(2)
      l4.SetLineStyle(10)
      l4.SetLineColor(ROOT.kRed)


      l1.Draw("same")
      l2.Draw("same")
      l3.Draw("same")
      l4.Draw("same")


      leg = ROOT.TLegend(0.55,0.6,0.85,0.48);
      leg.SetTextSize(0.035);
      leg.SetHeader('#splitline{p_{T}^{gen muon} #geq 25 GeV}{p_{T}^{L1 muon} #geq 20 GeV}')
      leg.Draw("same")

      ROOT.DrawPrelimLabel(canvas2)
      ROOT.DrawLumiLabel(canvas2,'%i PU'%puValue)
      ROOT.SaveCanvas(canvas2,'tdr_eta25_eff06'+ q+ str(puHandle))

      canvas8 = ROOT.CreateCanvas('name8',False,True)
      canvas8.cd()
      b['SingleMu_' + puHandle]['hEta7_15_q12_cut5'].SetName("hEta7_15_q12_cut5"+ puHandle)
      b['SingleMu_' + puHandle]['hEta7_15_q12_cut5'].Write()
      b['SingleMu_' + puHandle]['hEta7_15_q12_cut5'].Draw()
      b['SingleMu_' + puHandle]['hEta7_15_q12_cut5'].SetTitle(';Generated muon  #eta;Efficiency')
      canvas8.Update()
      graph = b['SingleMu_' + puHandle]['hEta7_15_q12_cut5'].GetPaintedGraph()
      graph.GetXaxis().SetRangeUser(0.,2.4)

      #canvas8.Update()

      #graph = b['SingleMu_' + puHandle]['hEta7_15_q12_cut5'].GetPaintedGraph()
      ##graph.SetMinimum(0.6)
      ##graph.SetMaximum(1.01)
      l1 = ROOT.TLine(0.82,0,0.82,1)
      l2 = ROOT.TLine(-0.82,0,-0.82,1)
      l3 = ROOT.TLine(1.23,0,1.23,1)
      l4 = ROOT.TLine(-1.23,0,-1.23,1)

      l1.SetLineWidth(2)
      l1.SetLineStyle(10)
      l1.SetLineColor(ROOT.kRed)

      l2.SetLineWidth(2)
      l2.SetLineStyle(10)
      l2.SetLineColor(ROOT.kRed)

      l3.SetLineWidth(2)
      l3.SetLineStyle(10)
      l3.SetLineColor(ROOT.kRed)

      l4.SetLineWidth(2)
      l4.SetLineStyle(10)
      l4.SetLineColor(ROOT.kRed)

      l1.Draw("same")
      l2.Draw("same")
      l3.Draw("same")
      l4.Draw("same")


      leg = ROOT.TLegend(0.55,0.6,0.85,0.48);
      leg.SetTextSize(0.025);
      leg.SetHeader('#splitline{7 GeV #leq p_{T}^{gen muon} #leq 15 GeV}{p_{T}^{L1 muon} #geq 5 GeV}')
      
      leg.Draw("same")

      ROOT.DrawPrelimLabel(canvas8)
      ROOT.DrawLumiLabel(canvas8,'%i PU'%puValue)
      ROOT.SaveCanvas(canvas8,'tdr_eta7_15_c5_eff'+ q + str(puHandle))


outFile.Close()
