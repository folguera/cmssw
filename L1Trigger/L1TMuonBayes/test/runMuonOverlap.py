# -*- coding: utf-8 -*-
import FWCore.ParameterSet.Config as cms

# General config options
import FWCore.ParameterSet.VarParsing as VarParsing
import sys

options = VarParsing.VarParsing()

options.register('globalTag',
                 '106X_upgrade2023_realistic_v2', #default value 
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.string,
                 "Global Tag")

options.register('Verbose',
                 False, #default value
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.bool,
                 "Dump logs")

options.register('addAging',
                 False, #default value
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.bool,
                 "Run re-emulation")

options.register('doPhase2TPs',
                 False, #default value
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.bool,
                 "do Phase2 Trigger primitives")


options.parseArguments()

import os
import sys
import commands

process = cms.Process("L1TMuonEmulation")

process.load("FWCore.MessageLogger.MessageLogger_cfi")

verbose = False

if options.Verbose:
    process.MessageLogger = cms.Service("MessageLogger",
                                        #suppressInfo       = cms.untracked.vstring('AfterSource', 'PostModule'),
                                        destinations   = cms.untracked.vstring(
                                            #'detailedInfo',
                                            #'critical',
                                            'cout',
                                            #'cerr',
                                            'omtfEventPrint'
                                        ),
                                        categories        = cms.untracked.vstring('l1tMuBayesEventPrint', 'OMTFReconstruction'),
                                        omtfEventPrint = cms.untracked.PSet(    
                                            extension = cms.untracked.string('.txt'),                
                                            threshold = cms.untracked.string('INFO'),
                                            default = cms.untracked.PSet( limit = cms.untracked.int32(0) ), 
                                            #INFO   =  cms.untracked.int32(0),
                                            #DEBUG   = cms.untracked.int32(0),
                                            l1tMuBayesEventPrint = cms.untracked.PSet( limit = cms.untracked.int32(1000000000) ),
                                            OMTFReconstruction = cms.untracked.PSet( limit = cms.untracked.int32(1000000000) )
                                        ),
                                        debugModules = cms.untracked.vstring(
                                            'L1TMuonBayesMuCorrelatorTrackProducer', 
                                            'OmtfTTAnalyzer',
                                            'simBayesOmtfDigis', 
                                            'omtfTTAnalyzer', 
                                            'simBayesMuCorrelatorTrackProducer'),
                                        
    )

#if not options.Verbose:
#    process.MessageLogger.cerr.FwkReport.reportEvery = cms.untracked.int32(-1)
#    process.options = cms.untracked.PSet(wantSummary = cms.untracked.bool(False)) 

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.Geometry.GeometryExtended2023D41Reco_cff')
process.load('Configuration.Geometry.GeometryExtended2023D41_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
#process.load('Configuration.StandardSequences.SimL1Emulator_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, options.globalTag, '')


process.source = cms.Source('PoolSource',
                            fileNames = cms.untracked.vstring(
                                '/store/mc/PhaseIITDRSpring19DR/Mu_FlatPt2to100-pythia8-gun/GEN-SIM-DIGI-RAW/PU200_106X_upgrade2023_realistic_v3-v2/70000/FFCFF986-ED0B-B74F-B253-C511D19B8249.root'),          
                            inputCommands = cms.untracked.vstring(
                                'keep *',
                                'drop l1tEMTFHit2016Extras_simEmtfDigis_CSC_HLT',
                                'drop l1tEMTFHit2016Extras_simEmtfDigis_RPC_HLT',
                                'drop l1tEMTFHit2016s_simEmtfDigis__HLT',
                                'drop l1tEMTFTrack2016Extras_simEmtfDigis__HLT',
                                'drop l1tEMTFTrack2016s_simEmtfDigis__HLT')
                        )
	                    
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1))


####Event Setup Producer
process.load('L1Trigger.L1TMuonBayes.fakeOmtfParams_cff')
process.esProd = cms.EDAnalyzer("EventSetupRecordDataGetter",
   toGet = cms.VPSet(
      cms.PSet(record = cms.string('L1TMuonOverlapParamsRcd'),
               data = cms.vstring('L1TMuonOverlapParams'))
                   ),
   verbose = cms.untracked.bool(False)
)

                                   
####OMTF Emulator
process.load('L1Trigger.L1TMuonBayes.simBayesOmtfDigis_cfi')

process.simBayesOmtfDigis.dumpResultToXML = cms.bool(True)
process.simBayesOmtfDigis.dumpResultToROOT = cms.bool(False)

process.simBayesOmtfDigis.rpcMaxClusterSize = cms.int32(3)
process.simBayesOmtfDigis.rpcMaxClusterCnt = cms.int32(2)
process.simBayesOmtfDigis.rpcDropAllClustersIfMoreThanMax = cms.bool(False)

#### load Phase-2 TPs
if options.doPhase2TPs:
    print 'Using Phase-2 Trigger primitives'

    process.load("Phase2L1Trigger.CalibratedDigis.CalibratedDigis_cfi") 
    process.load("L1Trigger.DTPhase2Trigger.dtTriggerPhase2PrimitiveDigis_cfi")

    process.CalibratedDigis.dtDigiTag = "simMuonDTDigis"
    process.CalibratedDigis.scenario = 0
    process.dtTriggerPhase2PrimitiveDigis.scenario = 0

    #Produce RPC clusters from RPCDigi
    process.load("RecoLocalMuon.RPCRecHit.rpcRecHits_cfi")
    process.rpcRecHits.rpcDigiLabel = cms.InputTag('simMuonRPCDigis')
    ##    # Use RPC
    ##    process.load('Configuration.Geometry.GeometryExtended2023D38Reco_cff')
    ##    process.load('Configuration.Geometry.GeometryExtended2023D38_cff')
    ##    process.dtTriggerPhase2PrimitiveDigis.useRPC = False
  
    process.dtTriggerPhase2PrimitiveDigis.max_quality_to_overwrite_t0 = 10 # strict inequality
    process.dtTriggerPhase2PrimitiveDigis.scenario = 0 # 0 for mc, 1 for data, 2 for slice test

    process.simBayesOmtfDigis.usePhase2TPs = cms.bool(False)
    process.simBayesOmtfDigis.srcDTP2Ph = cms.InputTag("dtTriggerPhase2PrimitiveDigis")
    
    
    process.L1TMuonSeq = cms.Sequence( process.esProd +      
                                       process.CalibratedDigis + 
                                       process.dtTriggerPhase2PrimitiveDigis + 
                                       process.simBayesOmtfDigis 
    )
else:
    process.L1TMuonSeq = cms.Sequence( process.esProd +      
                                       process.simBayesOmtfDigis 
    )



process.L1TMuonPath = cms.Path(process.L1TMuonSeq)

process.out = cms.OutputModule("PoolOutputModule", 
                               fileName = cms.untracked.string("l1tomtf.root"),
                               outputCommands=cms.untracked.vstring(
                                   'drop *',
                                   "keep *_simBayesOmtfDigis_OMTF_L1TMuonEmulation",
                                   "keep *_genParticles_*_*", 
                                   )
                               
)

process.output_step = cms.EndPath(process.out)
process.schedule = cms.Schedule(process.L1TMuonPath)
process.schedule.extend([process.output_step])
