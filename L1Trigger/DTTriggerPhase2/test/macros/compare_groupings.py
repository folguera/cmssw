#!/bin/env python
#
# PyROOT study of standard selector performance using sim-hit matching 
# to identify fake and signal muons
#
import os, re, ROOT, sys, pickle, time
from pprint import pprint
from math import *
from array import array
from DataFormats.FWLite import Events, Handle
import numpy as np


##
## User Input
##
def getPFNs(lfns):
    files = []
    for file in lfns:
        fullpath = "/eos/cms/" + file
        if os.path.exists(fullpath):
            files.append(fullpath)
        else:
            raise Exception("File not found: %s" % fullpath)
    return files


def IsMatched(muon1,muon2,sharedFrac=0.5):
    # first check if muon share Wh/Se/St 
    if (muon1.whNum()!=muon2.whNum()): return False 
    if (muon1.scNum()!=muon2.scNum()): return False 
    if (muon1.stNum()!=muon2.stNum()): return False     
    
    # now count the number of shared hits: 
    numShared=0.
    totMuon1=0.
    for ly in range(0,7):
        if (muon1.pathWireId(ly)>=0): 
            totMuon1=totMuon1+1. 
        else:   
            continue

        if (muon1.pathWireId(ly)!=muon2.pathWireId(ly)): continue
        if (muon1.pathTDC(ly)!=muon2.pathTDC(ly)): continue

        numShared = numShared+1.

    if (numShared/totMuon1 >= sharedFrac): return True

    return False

def hasPosRF(wh,sec): 
    return (wh > 0 or (wh == 0 and sec % 4 > 1))
    
def trigPhiInRad(trigPhi,sector):
    return trigPhi / 65536. * 0.8 + math.pi / 6 * (sector - 1);

def isMatchedToReco(mp,muon): 

    if (mp.whNum()!=muon.chamberId().wheel()): return False 
    seg_sec = muon.chamberId().sector()
    if   (muon.chamberId().sector() == 13): seg_sec = 4
    elif (muon.chamberId().sector() == 14): seg_sec = 10

    if (mp.scNum()!=seg_sec): return False 

    trigGlbPhi = trigPhiInRad(mp.phi(),mp.scNum())

    dphi       = muon.seg_posGlb_phi->at(iSeg) - trigGlbPhi;
    Double_t segTrigAMDPhi = abs(acos(cos(finalAMDPhi)));

    return True      
# files = getPFNs(lfns)

muoBayesHandle, muoBayesLabel = Handle("L1Phase2MuDTExtPhContainer"), ("dtTriggerPhase2BayesPrimitiveDigis","","L1DTTrigPhase2Prod")
muoStdHandle, muoStdLabel = Handle("L1Phase2MuDTExtPhContainer"), ("dtTriggerPhase2StdPrimitiveDigis","","L1DTTrigPhase2Prod")
muonRecoHandle,muonRecoLabel = Handle("edm::RangeMap<DTChamberId,edm::OwnVector<DTRecSegment4D>"),("dt4DSegments","","L1DTTrigPhase2Prod")
#edm::ClonePolicy<DTRecSegment4D> >,edm::ClonePolicy<DTRecSegment4D>>
#muonRecoHandle,muonRecoLabel = Handle("DTRecSegment4DCollection"),("dt4DSegments","","L1DTTrigPhase2Prod")
genHandle, genLabel = Handle("vector<reco::GenParticle>"), "genParticles"


ROOT.gROOT.SetBatch(True)

##
## Main part
##
files = ['/afs/cern.ch/user/f/folguera/workdir/Upgrade/DTTP/CMSSW_11_1_0_pre4_DTTPdev_Bayes/src/L1Trigger/DTTriggerPhase2/test/DTTriggerPhase2Primitives.root']

print "Number of files: %d" % len(files)
events = Events(files)    
print "we got the events" 
## load some histograms (and efficiencies): 
outputDict = {} 
dumpToFile = False

hPhiRes_q1 = []
hPhiRes_q3 = []
hPhiRes_q5 = []
hPhiRes_q8 = []

hPhiBRes_q1 = []
hPhiBRes_q3 = []
hPhiBRes_q5 = []
hPhiBRes_q8 = []

hChi2Res_q1 = []
hChi2Res_q3 = []
hChi2Res_q5 = []
hChi2Res_q8 = []

hBxRes_q1 = []
hBxRes_q3 = []
hBxRes_q5 = []
hBxRes_q8 = []

hTimeRes_q1 = []
hTimeRes_q3 = []
hTimeRes_q5 = []
hTimeRes_q8 = []

hMatchingEff = []
hNMatchedMPs = []

for algo in ["Bayes","Std"]:
    for st in range(1,5):    
        hMatchingEff.append(ROOT.TEfficiency("hMatchingEff_MB%i_%s" %(st,algo), "",9,0.5,9.5))
        hNMatchedMPs.append(ROOT.TEfficiency("hNMatchedMPs_MB%i_%s" %(st,algo), "",9,0.5,9.5))

        hPhiRes_q1.append(ROOT.TH1F("hPhiRes_MB%i_q1_%s" %(st,algo),"",20,-0.1,0.1))
        hPhiRes_q3.append(ROOT.TH1F("hPhiRes_MB%i_q3_%s" %(st,algo),"",20,-0.1,0.1))
        hPhiRes_q5.append(ROOT.TH1F("hPhiRes_MB%i_q5_%s" %(st,algo),"",20,-0.1,0.1))
        hPhiRes_q8.append(ROOT.TH1F("hPhiRes_MB%i_q8_%s" %(st,algo),"",20,-0.1,0.1))
        
        hPhiBRes_q1.append(ROOT.TH1F("hPhiBRes_MB%i_q1_%s" %(st,algo),"",20,-1.,1.))
        hPhiBRes_q3.append(ROOT.TH1F("hPhiBRes_MB%i_q3_%s" %(st,algo),"",20,-1.,1.))
        hPhiBRes_q5.append(ROOT.TH1F("hPhiBRes_MB%i_q5_%s" %(st,algo),"",20,-1.,1.))
        hPhiBRes_q8.append(ROOT.TH1F("hPhiBRes_MB%i_q8_%s" %(st,algo),"",20,-1.,1.))
        
        hChi2Res_q1.append(ROOT.TH1F("hChi2Res_MB%i_q1_%s" %(st,algo),"",20,-0.005,0.005))
        hChi2Res_q3.append(ROOT.TH1F("hChi2Res_MB%i_q3_%s" %(st,algo),"",20,-0.005,0.005))
        hChi2Res_q5.append(ROOT.TH1F("hChi2Res_MB%i_q5_%s" %(st,algo),"",20,-0.005,0.005))
        hChi2Res_q8.append(ROOT.TH1F("hChi2Res_MB%i_q8_%s" %(st,algo),"",20,-0.005,0.005))
        
        hBxRes_q1.append(ROOT.TH1F("hBxRes_MB%i_q1_%s" %(st,algo),"",20,-10,10.))
        hBxRes_q3.append(ROOT.TH1F("hBxRes_MB%i_q3_%s" %(st,algo),"",20,-10,10.))
        hBxRes_q5.append(ROOT.TH1F("hBxRes_MB%i_q5_%s" %(st,algo),"",20,-10,10.))
        hBxRes_q8.append(ROOT.TH1F("hBxRes_MB%i_q8_%s" %(st,algo),"",20,-10,10.))
        
        hTimeRes_q1.append(ROOT.TH1F("hTimeRes_MB%i_q1_%s" %(st,algo),"",20,-100,100.))
        hTimeRes_q3.append(ROOT.TH1F("hTimeRes_MB%i_q3_%s" %(st,algo),"",20,-100,100.))
        hTimeRes_q5.append(ROOT.TH1F("hTimeRes_MB%i_q5_%s" %(st,algo),"",20,-100,100.))
        hTimeRes_q8.append(ROOT.TH1F("hTimeRes_MB%i_q8_%s" %(st,algo),"",20,-100,100.))
        
for algo in ["Bayes","Std"]:
    outputDict[algo] = {}
    for st in range(1,5):
        idx = st-1:
        if "Std" in algo: idx = idx+4
        
        outputDict[algo]["hMatchingEff_MB%i"%st] = hMatchingEff[idx]
        outputDict[algo]["hNMatchedMPs_MB%i"%st] = hNMatchedMPs[idx]
        
        outputDict[algo]['hPhiRes_MB%i_q1'%st] = hPhiRes_q1[idx]
        outputDict[algo]['hPhiRes_MB%i_q3'%st] = hPhiRes_q3[idx]
        outputDict[algo]['hPhiRes_MB%i_q5'%st] = hPhiRes_q5[idx]
        outputDict[algo]['hPhiRes_MB%i_q8'%st] = hPhiRes_q8[idx]       
            
        outputDict[algo]['hPhiBRes_MB%i_q1'%st] = hPhiBRes_q1[idx]
        outputDict[algo]['hPhiBRes_MB%i_q3'%st] = hPhiBRes_q3[idx]
        outputDict[algo]['hPhiBRes_MB%i_q5'%st] = hPhiBRes_q5[idx]
        outputDict[algo]['hPhiBRes_MB%i_q8'%st] = hPhiBRes_q8[idx]
        
        outputDict[algo]['hChi2Res_MB%i_q1'%st] = hChi2Res_q1[idx]
        outputDict[algo]['hChi2Res_MB%i_q3'%st] = hChi2Res_q3[idx]
        outputDict[algo]['hChi2Res_MB%i_q5'%st] = hChi2Res_q5[idx]
        outputDict[algo]['hChi2Res_MB%i_q8'%st] = hChi2Res_q8[idx]       
        
        outputDict[algo]['hBxRes_MB%i_q1'%st] = hBxRes_q1[idx]
        outputDict[algo]['hBxRes_MB%i_q3'%st] = hBxRes_q3[idx]
        outputDict[algo]['hBxRes_MB%i_q5'%st] = hBxRes_q5[idx]
        outputDict[algo]['hBxRes_MB%i_q8'%st] = hBxRes_q8[idx]       
        
        outputDict[algo]['hTimeRes_MB%i_q1'%st] = hTimeRes_q1[idx]
        outputDict[algo]['hTimeRes_MB%i_q3'%st] = hTimeRes_q3[idx]
        outputDict[algo]['hTimeRes_MB%i_q5'%st] = hTimeRes_q5[idx]
        outputDict[algo]['hTimeRes_MB%i_q8'%st] = hTimeRes_q8[idx]       

# loop over events
print 'here :)'
count = 0

if (dumpTooFile): 
    f= open("EventDumpList.log","w+")

for ev in events:
    if not count%100:  print count, events.size()
    count = count+1
    ev.getByLabel(muonRecoLabel, muonRecoHandle)
    ev.getByLabel(muoBayesLabel, muoBayesHandle)
    ev.getByLabel(muoStdLabel, muoStdHandle)
    ev.getByLabel(genLabel, genHandle)
    
    muon_bayes = muoBayesHandle.product().getContainer()
    muon_std = muoStdHandle.product().getContainer()
    muons = muonRecoHandle.product()
    
    
    ## NOW PRINT MP TO FILE
    if (dumpToFile):
        f.write( "\nInspecting Event Number %i \n" %(ev.eventAuxiliary().id().event())  )
        f.write( "         Wh   Se   St  | w1 w2 w3 w4 w5 w6 w7 w8 |  tdc1  tdc2  tdc3  tdc4  tdc5  tdc6  tdc7  tdc8 | Q     phi  phib   chi2  bX\n" )
        f.write( "--------------------------------------------------------------------------------------------------------------------------------\n" )
        for muon in muon_bayes:
            f.write( "[Bayes]: Wh%2d Se%2d St%1d | %2d %2d %2d %2d %2d %2d %2d %2d | %5d %5d %5d %5d %5d %5d %5d %5d | Q%1d %6d %5d %7d %2d\n" %(muon.whNum(),muon.scNum(),muon.stNum(),muon.pathWireId(0),muon.pathWireId(1),muon.pathWireId(2),muon.pathWireId(3),muon.pathWireId(4),muon.pathWireId(5),muon.pathWireId(6),muon.pathWireId(7),muon.pathTDC(0),muon.pathTDC(1),muon.pathTDC(2),muon.pathTDC(3),muon.pathTDC(4),muon.pathTDC(5),muon.pathTDC(6),muon.pathTDC(7),muon.quality(),muon.phi(),muon.phiBend(),muon.chi2(),muon.bxNum()-20) )
        
        for muon in muon_std:
            f.write( "[Std  ]: Wh%2d Se%2d St%1d | %2d %2d %2d %2d %2d %2d %2d %2d | %5d %5d %5d %5d %5d %5d %5d %5d | Q%1d %6d %5d %7d %2d\n" %(muon.whNum(),muon.scNum(),muon.stNum(),muon.pathWireId(0),muon.pathWireId(1),muon.pathWireId(2),muon.pathWireId(3),muon.pathWireId(4),muon.pathWireId(5),muon.pathWireId(6),muon.pathWireId(7),muon.pathTDC(0),muon.pathTDC(1),muon.pathTDC(2),muon.pathTDC(3),muon.pathTDC(4),muon.pathTDC(5),muon.pathTDC(6),muon.pathTDC(7),muon.quality(),muon.phi(),muon.phiBend(),muon.chi2(), muon.bxNum()-20)  )
            
            
    ## NOW LOOP OVER RECO SEGMENTS AND MATCH TO MPs..
    for muon in muons:
        print muon.localPosition().x()
        print muon.chamberId().wheel()
        print muon.chamberId().station()
        print muon.chamberId().sector()
        
        
        ## Fill BAYES: 
        for mp in muon_bayes: 
            st = mp.stNum()-1
            quality = mp.quality()
            matched = IsMatchedToReco(mp,muon):
            
            hMatchingEff[st].Fill(matched, quality)
            
            if not matched: continue
                if (quality>=1) :  
                    hPhiRes_q1[st]  .Fill( float(mp.phi()-muon2.phi()) * 0.8 / 65536. )
                    hPhiBRes_q1[st] .Fill( float(mp.phiBend()-muon2.phiBend()) * 1.4 / 2048. )
                    hChi2Res_q1[st] .Fill( (mp.chi2()-muon2.chi2()) / 1000000. )
                    hBxRes_q1[st]   .Fill( (mp.bxNum()-muon2.bxNum()) )
                    hTimeRes_q1[st] .Fill( float(mp.t0()-muon2.t0()) )
                    
                if (quality>=3) :
                    hPhiRes_q3[st]  .Fill( float(mp.phi()-muon2.phi()) *0.8 / 65536.)
                    hPhiBRes_q3[st] .Fill( float(mp.phiBend()-muon2.phiBend()) * 1.4 / 2048. )
                    hChi2Res_q3[st] .Fill( (mp.chi2()-muon2.chi2()) / 1000000.)
                    hBxRes_q3[st]   .Fill( (mp.bxNum()-muon2.bxNum()) )
                    hTimeRes_q3[st] .Fill( float(mp.t0()-muon2.t0()) )

                if (quality>=5) :
                    hPhiRes_q5[st]  .Fill( float(mp.phi()-muon2.phi()) *0.8 / 65536. )
                    hPhiBRes_q5[st] .Fill( float(mp.phiBend()-muon2.phiBend()) * 1.4 / 2048.)
                    hChi2Res_q5[st] .Fill( (mp.chi2()-muon2.chi2())/ 1000000. )
                    hBxRes_q5[st]   .Fill( (mp.bxNum()-muon2.bxNum()) )
                    hTimeRes_q5[st] .Fill( float(mp.t0()-muon2.t0()) )
               
                if (quality>=8) :
                    hPhiRes_q8[st]  .Fill( float(mp.phi()-muon2.phi()) *0.8 / 65536.)
                    hPhiBRes_q8[st] .Fill( float(mp.phiBend()-muon2.phiBend()) * 1.4 / 2048.)
                    hChi2Res_q8[st] .Fill( (mp.chi2()-muon2.chi2()) / 1000000. )
                    hBxRes_q8[st]   .Fill( (mp.bxNum()-muon2.bxNum()) )
                    hTimeRes_q8[st] .Fill( float(mp.t0()-muon2.t0()) )
            

        
        ## Fill STD: 
        for mp in muon_std: 
            st = mp.stNum()-1+4 ## the +4 is to fill the correct histogram...
            quality = mp.quality()
            matched = IsMatchedToReco(mp,muon):
            
            hMatchingEff[st].Fill(matched, quality)


        



    if (dumpToFile): f.close()
    dumpToFile=False
    ev.toBegin()


import pickle 
with open('GroupingComparison_BayesToStd_Apr28.pickle', 'wb') as handle:
    pickle.dump(outputDict, handle, protocol=pickle.HIGHEST_PROTOCOL)
