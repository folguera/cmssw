# -*- coding: utf-8 -*-
import FWCore.ParameterSet.Config as cms
process = cms.Process("L1TMuonEmulation")
import os
import sys
import commands
import re
from os import listdir
from os.path import isfile, join

process.load("FWCore.MessageLogger.MessageLogger_cfi")

verbose = False

if verbose: 
    process.MessageLogger = cms.Service("MessageLogger",
       #suppressInfo       = cms.untracked.vstring('AfterSource', 'PostModule'),
       destinations   = cms.untracked.vstring(
                                               #'detailedInfo',
                                               #'critical',
                                               #'cout',
                                               #'cerr',
                                               'muCorrelatorEventPrint'
                    ),
       categories        = cms.untracked.vstring('l1tMuBayesEventPrint'),
       muCorrelatorEventPrint = cms.untracked.PSet(    
                         extension = cms.untracked.string('.txt'),                
                         threshold = cms.untracked.string('DEBUG'),
                         default = cms.untracked.PSet( limit = cms.untracked.int32(0) ), 
                         #INFO   =  cms.untracked.int32(0),
                         #DEBUG   = cms.untracked.int32(0),
                         l1tMuBayesEventPrint = cms.untracked.PSet( limit = cms.untracked.int32(100000000) )
                       ),
       debugModules = cms.untracked.vstring('L1TMuonBayesMuCorrelatorTrackProducer', 'OmtfTTAnalyzer', 'simOmtfDigis', 'omtfTTAnalyzer', 'simBayesMuCorrelatorTrackProducer') 
       #debugModules = cms.untracked.vstring('*')
    )

    #process.MessageLogger.cerr.FwkReport.reportEvery = cms.untracked.int32(100)
if not verbose:
    process.MessageLogger.cerr.FwkReport.reportEvery = cms.untracked.int32(1000)
    process.options = cms.untracked.PSet(wantSummary = cms.untracked.bool(False), 
                                         #SkipEvent = cms.untracked.vstring('ProductNotFound') 
                                     )


#######################################TTTracks################################################
GEOMETRY = "D17"

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.Geometry.GeometryExtended2023D17Reco_cff')
process.load('Configuration.Geometry.GeometryExtended2023D17_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.StandardSequences.SimL1Emulator_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

from Configuration.AlCa.GlobalTag import GlobalTag
#process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:upgradePLS3', '')
process.GlobalTag = GlobalTag(process.GlobalTag, '103X_upgrade2023_realistic_v2', '') 

############################################################
# input and output
############################################################

process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(-1))

# Source_Files = cms.untracked.vstring(
# #        "/store/relval/CMSSW_10_0_0_pre1/RelValTTbar_14TeV/GEN-SIM-DIGI-RAW/94X_upgrade2023_realistic_v2_2023D17noPU-v2/10000/06C888F3-CFCE-E711-8928-0CC47A4D764C.root"
#          #"/store/relval/CMSSW_9_3_2/RelValTTbar_14TeV/GEN-SIM-DIGI-RAW/93X_upgrade2023_realistic_v2_2023D17noPU-v1/10000/0681719F-AFA6-E711-87C9-0CC47A4C8E14.root"
#          #"file:///eos/user/k/kbunkow/cms_data/0681719F-AFA6-E711-87C9-0CC47A4C8E14.root"
#          #"file:///eos/cms/store/group/upgrade/sandhya/SMP-PhaseIIFall17D-00001.root"
#          #'file:///afs/cern.ch/work/k/kbunkow/private/omtf_data/SingleMu_15_p_1_1_qtl.root' no high eta in tis file
#          'file:///eos/user/k/kbunkow/cms_data/SingleMuFullEta/721_FullEta_v4/SingleMu_12_p_10_1_mro.root' ,
#          'file:///eos/user/k/kbunkow/cms_data/SingleMuFullEta/721_FullEta_v4/SingleMu_20_p_118_1_sTk.root' ,
#          'file:///eos/user/k/kbunkow/cms_data/SingleMuFullEta/721_FullEta_v4/SingleMu_5_p_81_1_Ql3.root',
#          'file:///eos/user/k/kbunkow/cms_data/SingleMuFullEta/721_FullEta_v4/SingleMu_6_p_4_2_gCH.root',
#          'file:///eos/user/k/kbunkow/cms_data/SingleMuFullEta/721_FullEta_v4/SingleMu_31_p_89_2_MJS.root',
#         #'file:///afs/cern.ch/work/k/kbunkow/public/CMSSW/cmssw_10_x_x_l1tOfflinePhase2/CMSSW_10_1_7/src/L1Trigger/L1TMuonBayes/test/F4EEAE55-C937-E811-8C29-48FD8EE739D1_dump1000Events.root'
#          #"/store/mc/PhaseIIFall17D/SingleMu_FlatPt-2to100/GEN-SIM-DIGI-RAW/L1TnoPU_93X_upgrade2023_realistic_v5-v1/00000/F4EEAE55-C937-E811-8C29-48FD8EE739D1.root"
# )


#path = '/eos/user/k/kbunkow/cms_data/SingleMuFullEta/721_FullEta_v4/'
#path = '/afs/cern.ch/work/a/akalinow/public/MuCorrelator/Data/SingleMu/9_3_14_FullEta_v1/'
#path = '/eos/user/a/akalinow/Data/SingleMu/9_3_14_FullEta_v1/'
path = '/eos/user/a/akalinow/Data/SingleMu/9_3_14_FullEta_v2/'
#path = '/afs/cern.ch/work/k/kbunkow/public/data/SingleMuFullEta/721_FullEta_v4/'

onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
#print onlyfiles

filesNameLike = sys.argv[2]
#chosenFiles = ['file://' + path + f for f in onlyfiles if (('_p_10_' in f) or ('_m_10_' in f))]
#chosenFiles = ['file://' + path + f for f in onlyfiles if (('_10_p_10_' in f))]
#chosenFiles = ['file://' + path + f for f in onlyfiles if (re.match('.*_._p_10.*', f))]
#chosenFiles = ['file://' + path + f for f in onlyfiles if ((filesNameLike in f))]

#print onlyfiles

chosenFiles = []

filesPerPtBin = 100

if filesNameLike == 'allPt' :
    for ptCode in range(31, 3, -1) :
        for sign in ['_m', '_p'] : #, m
            selFilesPerPtBin = 0
            for i in range(1, 101, 1): #TODO
                for f in onlyfiles:
                   #if (( '_' + str(ptCode) + sign + '_' + str(i) + '_') in f): 
                   if (( '_' + str(ptCode) + sign + '_' + str(i) + ".") in f): 
                        #print f
                        chosenFiles.append('file://' + path + f) 
                        selFilesPerPtBin += 1
                if(selFilesPerPtBin >= filesPerPtBin):
                    break
                        
else :
    for i in range(1, 2, 1):
        for f in onlyfiles:
            #if (( filesNameLike + '_' + str(i) + '_') in f): 
            if (( filesNameLike + '_' + str(i) + '.') in f): 
                print f
                chosenFiles.append('file://' + path + f) 
         

print "chosenFiles"
for chFile in chosenFiles:
    print chFile

if len(chosenFiles) == 0 :
    print "no files selected!!!!!!!!!!!!!!!"
    exit

firstEv = 0#40000
nEvents = 100000

# input files (up to 255 files accepted)
process.source = cms.Source('PoolSource',
fileNames = cms.untracked.vstring( 
    #'file:/eos/user/k/kbunkow/cms_data/SingleMuFullEta/721_FullEta_v4/SingleMu_16_p_1_1_xTE.root',
    #'file:/afs/cern.ch/user/k/kpijanow/Neutrino_Pt-2to20_gun_50.root',
    list(chosenFiles),
                                  ),
# eventsToProcess = cms.untracked.VEventRange(
#  '3:' + str(firstEv) + '-3:' +   str(firstEv + nEvents),
#  '4:' + str(firstEv) + '-4:' +   str(firstEv + nEvents),
#  '5:' + str(firstEv) + '-5:' +   str(firstEv + nEvents),
#  '6:' + str(firstEv) + '-6:' +   str(firstEv + nEvents),
#  '7:' + str(firstEv) + '-7:' +   str(firstEv + nEvents),
#  '8:' + str(firstEv) + '-8:' +   str(firstEv + nEvents),
#  '9:' + str(firstEv) + '-9:' +   str(firstEv + nEvents),
# '10:' + str(firstEv) + '-10:' +  str(firstEv + nEvents),
# '11:' + str(firstEv) + '-11:' +  str(firstEv + nEvents),
# '12:' + str(firstEv) + '-12:' +  str(firstEv + nEvents),
# '13:' + str(firstEv) + '-13:' +  str(firstEv + nEvents),
# '14:' + str(firstEv) + '-14:' +  str(firstEv + nEvents),
# '15:' + str(firstEv) + '-15:' +  str(firstEv + nEvents),
# '16:' + str(firstEv) + '-16:' +  str(firstEv + nEvents),
# '17:' + str(firstEv) + '-17:' +  str(firstEv + nEvents),
# '18:' + str(firstEv) + '-18:' +  str(firstEv + nEvents),
# '19:' + str(firstEv) + '-19:' +  str(firstEv + nEvents),
# '20:' + str(firstEv) + '-20:' +  str(firstEv + nEvents),
# '21:' + str(firstEv) + '-21:' +  str(firstEv + nEvents),
# '22:' + str(firstEv) + '-22:' +  str(firstEv + nEvents),
# '23:' + str(firstEv) + '-23:' +  str(firstEv + nEvents),
# '24:' + str(firstEv) + '-24:' +  str(firstEv + nEvents),
# '25:' + str(firstEv) + '-25:' +  str(firstEv + nEvents),
# '26:' + str(firstEv) + '-26:' +  str(firstEv + nEvents),
# '27:' + str(firstEv) + '-27:' +  str(firstEv + nEvents),
# '28:' + str(firstEv) + '-28:' +  str(firstEv + nEvents),
# '29:' + str(firstEv) + '-29:' +  str(firstEv + nEvents),
# '30:' + str(firstEv) + '-30:' +  str(firstEv + nEvents),
# '31:' + str(firstEv) + '-31:' +  str(firstEv + nEvents)),
skipEvents =  cms.untracked.uint32(0),

        inputCommands=cms.untracked.vstring(
        'keep *',
        'drop l1tEMTFHit2016Extras_simEmtfDigis_CSC_HLT',
        'drop l1tEMTFHit2016Extras_simEmtfDigis_RPC_HLT',
        'drop l1tEMTFHit2016s_simEmtfDigis__HLT',
        'drop l1tEMTFTrack2016Extras_simEmtfDigis__HLT',
        'drop l1tEMTFTrack2016s_simEmtfDigis__HLT')
)

# PostLS1 geometry used TODO is this correct geometry for the phase 2?
#process.load('Configuration.Geometry.GeometryExtended2015Reco_cff')
#process.load('Configuration.Geometry.GeometryExtended2015_cff')
############################
#process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')
#from Configuration.AlCa.GlobalTag_condDBv2 import GlobalTag
#process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_mc', '')

####OMTF Emulator
process.load('L1Trigger.L1TMuonBayes.simBayesMuCorrelatorTrackProducer_cfi')

process.dumpED = cms.EDAnalyzer("EventContentAnalyzer")
process.dumpES = cms.EDAnalyzer("PrintEventSetupContent")

process.TFileService = cms.Service("TFileService", fileName = cms.string('muCorrelatorHistsSimTracks100Files_t9.root'), closeFileFast = cms.untracked.bool(True))

process.simBayesMuCorrelatorTrackProducer.g4SimTrackSrc = cms.InputTag('g4SimHits')
process.simBayesMuCorrelatorTrackProducer.ttTracksSource = cms.string("SIM_TRACKS")
process.simBayesMuCorrelatorTrackProducer.pdfModuleType = cms.string("PdfModuleWithStats") #TODO
process.simBayesMuCorrelatorTrackProducer.minDtPhQuality = cms.int32(4);
process.simBayesMuCorrelatorTrackProducer.generatePdfs = cms.bool(True);
process.simBayesMuCorrelatorTrackProducer.outPdfModuleFile = cms.string("pdfModuleSimTracks100FilesSigma1p3_t9.xml") #TODO
process.simBayesMuCorrelatorTrackProducer.generateTiming = cms.bool(False)

process.simBayesMuCorrelatorTrackProducer.lctCentralBx = cms.int32(6);#<<<<<<<<<<<<<<<<!!!!!!!!!!!!!!!!!!!!TODO this was changed in CMSSW 10(?) to 8. if the data were generated with the previous CMSSW then you have to use 6


process.L1TMuonSeq = cms.Sequence( #process.esProd +         
                                   process.simBayesMuCorrelatorTrackProducer 
                                   #+ process.dumpED
                                   #+ process.dumpES
)

process.L1TMuonPath = cms.Path(process.L1TMuonSeq)

# process.out = cms.OutputModule("PoolOutputModule", 
#    fileName = cms.untracked.string("l1tomtf_superprimitives1.root")
# )
#process.output_step = cms.EndPath(process.out)


############################################################

# use this if you want to re-run the stub making
#process.schedule = cms.Schedule(process.TTClusterStub,process.TTClusterStubTruth,process.TTTracksWithTruth,process.ana)

# use this if cluster/stub associators not available 
process.schedule = cms.Schedule(process.L1TMuonPath)

# use this to only run tracking + track associator
#process.schedule = cms.Schedule(process.TTTracksWithTruth,process.ana)

#process.schedule.extend([process.output_step])
