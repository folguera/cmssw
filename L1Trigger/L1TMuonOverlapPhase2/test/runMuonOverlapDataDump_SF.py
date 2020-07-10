# -*- coding: utf-8 -*-
import FWCore.ParameterSet.Config as cms
process = cms.Process("L1TMuonEmulation")
import os
import sys
import commands

process.load("FWCore.MessageLogger.MessageLogger_cfi")

dumpHitsFileName = 'OMTFHits2_pats0x00031_newerSample_files_1_100' #'OMTFHits_pats0x00031_newerSample_files_1_100' OMTFHits_pats0x0003_oldSample_files_30_40
process.MessageLogger = cms.Service("MessageLogger",
    destinations   = cms.untracked.vstring(
                                               #'detailedInfo',
                                               #'critical',
                                               #'cout',
                                               #'cerr',
                                               'omtfEventPrint'
    ),
    categories        = cms.untracked.vstring('l1tMuBayesEventPrint', 'OMTFReconstruction'),
    omtfEventPrint = cms.untracked.PSet(    
                         filename  = cms.untracked.string('log_events'),
                         extension = cms.untracked.string('.txt'),                
                         threshold = cms.untracked.string('DEBUG'),
                         default = cms.untracked.PSet( limit = cms.untracked.int32(0) ), 
                         #INFO   =  cms.untracked.int32(0),
                         #DEBUG   = cms.untracked.int32(0),
                         l1tMuBayesEventPrint = cms.untracked.PSet( limit = cms.untracked.int32(1000000000) ),
                         OMTFReconstruction = cms.untracked.PSet( limit = cms.untracked.int32(1000000000) ) 
    ),
    debugModules = cms.untracked.vstring('L1TMuonBayesMuCorrelatorTrackProducer', 'OmtfTTAnalyzer', 'simBayesOmtfDigis', 'omtfTTAnalyzer', 'simBayesMuCorrelatorTrackProducer') 
)


process.options = cms.untracked.PSet(wantSummary = cms.untracked.bool(False))

process.source = cms.Source('PoolSource',
                            fileNames = cms.untracked.vstring("file:///eos/cms/store/user/folguera/P2L1TUpgrade/Mu_FlatPt2to100-pythia8-gun_file.root")
)
	                    
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(100))

# PostLS1 geometry used
process.load('Configuration.Geometry.GeometryExtended2015Reco_cff')
process.load('Configuration.Geometry.GeometryExtended2015_cff')
############################
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')
from Configuration.AlCa.GlobalTag_condDBv2 import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_mc', '')


####Event Setup Producer
process.load('L1Trigger.L1TMuonOverlapPhase1.fakeOmtfParams_cff')
process.esProd = cms.EDAnalyzer("EventSetupRecordDataGetter",
   toGet = cms.VPSet(
      cms.PSet(record = cms.string('L1TMuonOverlapParamsRcd'),
               data = cms.vstring('L1TMuonOverlapParams'))
                   ),
   verbose = cms.untracked.bool(False)
)

process.TFileService = cms.Service("TFileService", fileName = cms.string('omtfAnalysis1.root'), closeFileFast = cms.untracked.bool(True) )

### DT Phase-2 trigger primitives
process.load("L1Trigger.DTTriggerPhase2.CalibratedDigis_cfi")		
process.load("L1Trigger.DTTriggerPhase2.dtTriggerPhase2PrimitiveDigis_cfi")		

process.CalibratedDigis.dtDigiTag = "simMuonDTDigis"
process.CalibratedDigis.scenario = 0
process.dtTriggerPhase2PrimitiveDigis.scenario = 0

process.dtTriggerPhase2PrimitiveDigis.max_quality_to_overwrite_t0 = 10 # strict inequality
process.dtTriggerPhase2PrimitiveDigis.scenario = 0 # 0 for mc, 1 for data, 2 for slice test
								
####OMTF Emulator
process.load('L1Trigger.L1TMuonOverlapPhase2.simOmtfPhase2Digis_cfi')

process.simOmtfPhase2Digis.dumpResultToXML = cms.bool(True)
process.simOmtfPhase2Digis.dumpResultToROOT = cms.bool(True)
process.simOmtfPhase2Digis.eventCaptureDebug = cms.bool(True)
process.simOmtfPhase2Digis.dumpHitsToROOT = cms.bool(True)
process.simOmtfPhase2Digis.dumpHitsFileName = cms.string(dumpHitsFileName + '.root')
process.simOmtfPhase2Digis.rpcMaxClusterSize = cms.int32(3)
process.simOmtfPhase2Digis.rpcMaxClusterCnt = cms.int32(2)
process.simOmtfPhase2Digis.rpcDropAllClustersIfMoreThanMax = cms.bool(True)

process.simOmtfPhase2Digis.lctCentralBx = cms.int32(8);#<<<<<<<<<<<<<<<<!!!!!!!!!!!!!!!!!!!!TODO this was changed in CMSSW 10(?) to 8. if the data were generated with the previous CMSSW then you have to use 6

process.dumpED = cms.EDAnalyzer("EventContentAnalyzer")
process.dumpES = cms.EDAnalyzer("PrintEventSetupContent")

process.L1TMuonSeq = cms.Sequence( process.esProd          
                                   + process.CalibratedDigis
                                   + process.dtTriggerPhase2PrimitiveDigis
                                   + process.simOmtfPhase2Digis 
                                   #+ process.dumpED
                                   #+ process.dumpES
)

process.L1TMuonPath = cms.Path(process.L1TMuonSeq)

process.out = cms.OutputModule("PoolOutputModule", 
                               fileName = cms.untracked.string("l1tomtf_superprimitives_P2TPs.root"),
                               outputCommands=cms.untracked.vstring(
                                   'drop *',
                                   "keep *_dtTrigger*_*_*",
                                   "keep *_simDtTrigger*_*_*",
                                   "keep *_simOmtfPhase2Digis_OMTF_L1TMuonEmulation",
                                   "keep *_genParticles_*_*", 
                                   )
)

process.output_step = cms.EndPath(process.out)
process.schedule = cms.Schedule(process.L1TMuonPath)
process.schedule.extend([process.output_step])
