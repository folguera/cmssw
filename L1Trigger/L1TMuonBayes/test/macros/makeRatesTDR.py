#!/bin/env python
#
#

import os, re, ROOT, sys, pickle, time
from pprint import pprint
from math import *
from array import array
from DataFormats.FWLite import Events, Handle
import numpy as np

datasets = { 
    #'Nu_PU140'       : { 'path' : '/eos/cms/store/group/phys_muon/sesanche/overlap_sep20/Nu_E10-pythia8-gun/Nu_PU140/', 'total':0              },
    'Nu_PU200'       : { 'path' : '/eos/cms/store/user/folguera/OMTF/Feb20_P1TP/Mu_FlatPt2to100-pythia8-gun/crab_L1MuPhase2Ntuples_Mu_FlatPt2to100_PU200/200204_162831/0000/', 'total':0},   
#    'Nu_PU200_aged1000'       : { 'path' : '/eos/cms/store/group/phys_muon/cericeci/overlap_oct22/Nu_E10-pythia8-gun/Nu_PU200/191103_163451/', 'total':0              },
#    'Nu_PU200_aged3000'       : { 'path' : '/eos/cms/store/group/phys_muon/cericeci/overlap_oct22/Nu_E10-pythia8-gun/Nu_PU200/191104_095521/', 'total':0              },
    #'Nu_PU250'       : { 'path' : '/eos/cms/store/group/phys_muon/sesanche/overlap_sep20/Nu_E10-pythia8-gun/Nu_PU250/', 'total':0              },    
    #'Nu_PU300'       : { 'path' : '/eos/cms/store/group/phys_muon/cericeci/overlap_sep20/Nu_E10-pythia8-gun/Nu_PU300/', 'total':0              },  
}

bins =  [0.,1.,2.,3.,4.,4.5,5.,6.,7.,8.,10.,12.,14.,16.,18.,20.,25.,30.,35.,40.,45.,50.,60.,70.,80.,90.,100.,120.,140.,200.]


def getEta(etaHW):
    return  etaHW/240.*2.61

def getPt(ptHW):
    return (ptHW-1.)/2.

def modulo(val):
    while val > 2*pi: val -= 2*pi
    while val <0: val += 2*pi
    return val

def getPhi(obj):
    return modulo(((15.+obj.processor()*60.)/360. + obj.hwPhi()/576.)*2*pi)

def getP4(obj):
    pt = obj.pt()
    eta= obj.eta()
    phi= obj.phi()
    v = ROOT.TLorentzVector()
    v.SetPtEtaPhiM( pt, eta, phi, 0)
    return v

def getP4FromHW(obj):
    pt = obj.hwPt()
    eta= obj.hwEta()
    phi= obj.hwPhi()
    v = ROOT.TLorentzVector()
    v.SetPtEtaPhiM( getPt(pt), getEta(eta), getPhi(obj), 0)
    return v



outputDict = {} 


for dataset in datasets:
    thefiles = [] 
    outputDict[dataset] = {}
    for subdir, dirs, files in os.walk(datasets[dataset]['path']):
        fil = filter( lambda x : '.root' in x and "l1tomtf" in x, files)
        for f in fil: thefiles.append( subdir + '/' + f)
    datasets[dataset]['files'] = thefiles
    outputDict[dataset]['total'] = 0 
    for b in bins:
        outputDict[dataset]['fired' + str(b) + "_q12"] = 0
        outputDict[dataset]['fired' + str(b) + "_q4"] = 0
        outputDict[dataset]['fired' + str(b) + "_q0"] = 0

        
muonHandle, muonLabel = Handle("BXVector<l1t::RegionalMuonCand>"), ("simBayesOmtfDigis", "OMTF", "L1TMuonEmulation" )


maxEvents = -1

for dataset in datasets:
    print 'starting to process', dataset
    events = Events(datasets[dataset]['files'])
    print 'we got the events'
    count = 0
    for ev in events:
        if not count%1000:  print count, events.size()
        count += 1
        outputDict[dataset]['total'] = outputDict[dataset]['total'] + 1 
        ev.getByLabel(muonLabel, muonHandle)
        muons = muonHandle.product()
        goodIndex = 0
        for bxNumber in range(muons.getFirstBX(), muons.getLastBX()+1):
            size = muons.size(bxNumber)
            for i in range(size):
                muon = muons[i+goodIndex]
                if muon.trackFinderType() not in [1,2]: continue
                
                for b in bins:
                    if getPt(muon.hwPt()) >= b:
                        if muon.hwQual() >= 12:
                            outputDict[dataset]['fired'+str(b) + "_q12"] = outputDict[dataset]['fired'+str(b)+ "_q12"] + 1 
                        if muon.hwQual() >= 4:
                            outputDict[dataset]['fired'+str(b) + "_q4"] = outputDict[dataset]['fired'+str(b)+ "_q4"] + 1 
                        if muon.hwQual() >= 0:
                            outputDict[dataset]['fired'+str(b) + "_q0"] = outputDict[dataset]['fired'+str(b)+ "_q0"] + 1 

            goodIndex = goodIndex + size


import pickle 
with open('tdr_rates_aged_all.pickle', 'wb') as handle:
    pickle.dump(outputDict, handle, protocol=pickle.HIGHEST_PROTOCOL)

