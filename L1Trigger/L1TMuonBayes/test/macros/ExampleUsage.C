// Example usage of the plotting template (originally used for TRG-17-001)
// Author: O. Davignon (CERN)
#include "PlotTemplate.C"

void ExampleUsage()
{
  // Example of how to use PlotTemplate.C

  // Modify the present script, then run using:
  // root -l
  // [0] .L ExampleUsage.C++
  // [1] ExampleUsage()

  gStyle->SetOptStat(000000);

  TString PlotName = "myPlotName";
  bool LogY = true;
  bool DisplayGrid = true;
  TString Lumi = "35.9";

  TCanvas* myCanvas = CreateCanvas(PlotName, LogY, DisplayGrid);

  //here add the histos, functions, etc. you want to draw (drawing happens below)

  double minimumX = 0.;
  double maximumX = 1.;
  double minimumY = 5.;
  double maximumY = 200.;

  // follows are two dummy examples of a function / a histo
  TF1* myFunction = new TF1("myFunction","x *100",minimumX,maximumX);
  myFunction->SetTitle("");

  // TH1F* myFunction = new TH1F("myFunction","myFuncion",100,minimumX,maximumX);
  // for(Int_t i = 1 ; i <= myFunction->GetNbinsX() ; ++i) myFunction->SetBinContent(i,100+float(i));
  // myFunction->SetTitle("");

  // when you read file(s) where histos / graphs are saved
  // TFile myFileContainingHistos("filename.root","READ");
  // myFunction = (TH1F*)myFileContainingHistos.Get("histoName");

  // follows are examples on how to format legends, axis, etc.

  //axis labels ranges & names
  if(LogY && minimumY==0.) cout<<"****** LogY == true and minimumY == 0, you probably want to avoid that ******"<<endl;
  myFunction->SetMinimum(minimumY);
  myFunction->SetMaximum(maximumY);
  myFunction->GetXaxis()->SetRangeUser(minimumX,maximumX);
  myFunction->GetYaxis()->SetTitle("y-axis title [unit]");
  myFunction->GetXaxis()->SetTitle("x-axis title [unit]");
  myFunction->GetXaxis()->SetTitleOffset(1.2);
  myFunction->GetYaxis()->SetTitleOffset(1.4);

  //line style  
  myFunction->SetLineColor(kBlue);
  myFunction->SetLineWidth(3);

  //drawing
  myFunction->Draw();

  //legend
  TLegend* leg = new TLegend(0.14,0.76,0.75,0.86);
  //leg->SetBorderSize(0);
  //leg->SetFillStyle(0);
  leg->SetTextSize(0.035);
  //leg->SetHeader("here is a beautiful header");
  leg->AddEntry(myFunction,"description of myFunction");
  leg->Draw("same");

  //line
  // double max_line = 115.;
  // TLine* a_line = new TLine(0.,max_line,1.,max_line);
  // a_line->SetLineColor(kRed);
  // a_line->SetLineWidth(3.);
  // a_line->SetLineStyle(2);
  // a_line->Draw("same");

  DrawPrelimLabel(myCanvas);
  DrawLumiLabel(myCanvas, Lumi);
  SaveCanvas(myCanvas, PlotName);

  return;

}
