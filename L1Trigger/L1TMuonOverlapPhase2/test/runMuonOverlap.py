# -*- coding: utf-8 -*-
import FWCore.ParameterSet.Config as cms
process = cms.Process("L1TMuonEmulation")
import os
import sys
import commands

process.load("FWCore.MessageLogger.MessageLogger_cfi")

process.MessageLogger.cerr.FwkReport.reportEvery = cms.untracked.int32(50)
process.options = cms.untracked.PSet(wantSummary = cms.untracked.bool(False))

process.source = cms.Source('PoolSource',
 #fileNames = cms.untracked.vstring('file:/afs/cern.ch/work/g/gflouris/public/SingleMuPt6180_noanti_10k_eta1.root')
 #fileNames = cms.untracked.vstring('file:///afs/cern.ch/work/k/kbunkow/private/omtf_data/SingleMu_15_p_1_1_qtl.root')    
 #fileNames = cms.untracked.vstring('file:///eos/user/k/kbunkow/cms_data/mc/PhaseIIFall17D/SingleMu_PU200_32DF01CC-A342-E811-9FE7-48D539F3863E_dump500Events.root')
 fileNames = cms.untracked.vstring("file:///eos/user/k/kbunkow/cms_data/mc/PhaseIITDRSpring19DR/PhaseIITDRSpring19DR_Mu_FlatPt2to100_noPU_v31_E0D5C6A5-B855-D14F-9124-0B2C9B28D0EA_dump4000Ev.root")                     
 )
	                    
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(1000))

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
		
#TODO
#process.load("L1Trigger.DTTriggerPhase2.dtTriggerPhase2PrimitiveDigis_cfi")
#process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
#process.load("Configuration.StandardSequences.MagneticField_AutoFromDBCurrent_cff")
#process.GlobalTag.globaltag = "90X_dataRun2_Express_v2"
#process.GlobalTag.globaltag = "80X_dataRun2_2016SeptRepro_v7"
#process.GlobalTag.globaltag = "100X_upgrade2018_realistic_v10"

#Calibrate Digis
process.load("L1Trigger.DTTriggerPhase2.CalibratedDigis_cfi")
#process.CalibratedDigis.flat_calib = 325 #turn to 0 to use the DB  , 325 for JM and Jorge benchmark
process.CalibratedDigis.dtDigiTag = "simMuonDTDigis" #turn to 0 to use the DB  , 325 for JM and Jorge benchmark
process.CalibratedDigis.scenario = 0 # 0 for mc, 1 for data, 2 for slice test

#DTTriggerPhase2
process.load("L1Trigger.DTTriggerPhase2.dtTriggerPhase2PrimitiveDigis_cfi")
#process.dtTriggerPhase2PrimitiveDigis.trigger_with_sl = 3  #4 means SL 1 and 3
#for the moment the part working in phase2 format is the slice test
#process.dtTriggerPhase2PrimitiveDigis.p2_df = True
#process.dtTriggerPhase2PrimitiveDigis.filter_primos = True
#for debugging
#process.dtTriggerPhase2PrimitiveDigis.pinta = True
#process.dtTriggerPhase2PrimitiveDigis.min_phinhits_match_segment = 4
#process.dtTriggerPhase2PrimitiveDigis.debug = True
process.dtTriggerPhase2PrimitiveDigis.scenario = 0
process.dtTriggerPhase2PrimitiveDigis.dump = True
	
								
####OMTF Emulator
process.load('L1Trigger.L1TMuonOverlapPhase2.simOmtfPhase2Digis_cfi')

process.simOmtfPhase2Digis.dumpResultToXML = cms.bool(True)
process.simOmtfPhase2Digis.rpcMaxClusterSize = cms.int32(3)
process.simOmtfPhase2Digis.rpcMaxClusterCnt = cms.int32(2)
process.simOmtfPhase2Digis.rpcDropAllClustersIfMoreThanMax = cms.bool(False)

process.simOmtfPhase2Digis.lctCentralBx = cms.int32(8);#<<<<<<<<<<<<<<<<!!!!!!!!!!!!!!!!!!!!TODO this was changed in CMSSW 10(?) to 8. if the data were generated with the previous CMSSW then you have to use 6

process.simOmtfPhase2Digis.dropDTPrimitives = cms.bool(True)
process.simOmtfPhase2Digis.usePhase2DTPrimitives = cms.bool(True)

process.dumpED = cms.EDAnalyzer("EventContentAnalyzer")
process.dumpES = cms.EDAnalyzer("PrintEventSetupContent")

process.L1TMuonSeq = cms.Sequence( process.esProd          
                                   + process.simOmtfPhase2Digis 
                                   #+ process.dumpED
                                   #+ process.dumpES
)

process.L1TMuonPath = cms.Path(process.CalibratedDigis * 
							process.dtTriggerPhase2PrimitiveDigis * process.L1TMuonSeq)

process.out = cms.OutputModule("PoolOutputModule", 
   fileName = cms.untracked.string("l1tomtf_superprimitives1.root")
)

#process.output_step = cms.EndPath(process.out)
#process.schedule = cms.Schedule(process.L1TMuonPath)
#process.schedule.extend([process.output_step])
