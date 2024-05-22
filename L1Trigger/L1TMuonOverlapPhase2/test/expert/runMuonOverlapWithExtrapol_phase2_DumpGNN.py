# -*- coding: utf-8 -*-
import FWCore.ParameterSet.Config as cms
import os
import sys

from os import listdir
from os.path import isfile, join
import fnmatch

import FWCore.ParameterSet.VarParsing as VarParsing

# setup any defaults you want
options = VarParsing.VarParsing( 'analysis' )

options.register('verbose',False, VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.bool, "Activate Verbosity")
options.register('dump', False, VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.bool, "Activate dump")
options.register('useNN', True, VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.bool, "Activate Neural Network")
options.register('minDtPhiQuality', 2, VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.int, "Minimum Quality for Phi")
options.register('minDtPhiBQuality', 2, VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.int, "Minimum Quality for PhiB")
options.register('useExtrapolationAlgo', True, VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.bool, "Activate Extrapolation Algorithm")
options.register('version', 't22__', VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.string, "Version")
options.register('matchUsingPropagator', False, VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.bool, "Match using Propagator (false for SingleMu without PU)")

options.outputFile = 'l1tomtf.root'
#options.inputFiles = 'file:/eos/cms/store/user/folguera/OMTF/MuonGunSample_106X/MuonFlatPt1to1000_1001_numEvent2000.root'
options.inputFiles = 'file:///eos/user/a/akalinow/Data/SingleMu/13_1_0_03_01_2024/SingleMu_ch0_OneOverPt_Run2029_13_1_0_03_01_2024/13_1_0_03_01_2024/240103_094044/0000/SingleMu_OneOverPt_1_100_m_11.root'

# get and parse the command line arguments
options.parseArguments()

process = cms.Process("L1TMuonEmulation")
process.load("FWCore.MessageLogger.MessageLogger_cfi")

version=options.version

if options.useExtrapolationAlgo :
    version = version + 'Patterns_ExtraplMB1nadMB2DTQualAndEtaFixedP_ValueP1Scale_t20_v1_SingleMu_iPt_and_OneOverPt_classProb17_recalib2_minDP0'
else :
    version = version + 'Patterns_0x00012'

outFilesName = "TestEvents__" + version

if options.useNN :
   version = version + "_NN_FP_v217"

if options.verbose: 
    process.MessageLogger = cms.Service("MessageLogger",
       #suppressInfo       = cms.untracked.vstring('AfterSource', 'PostModule'),
       destinations   = cms.untracked.vstring(
                                               #'detailedInfo',
                                               #'critical',
                                               #'cout',
                                               #'cerr',
                                               'omtfEventPrint'
                    ),
       categories        = cms.untracked.vstring( 'OMTFReconstruction', 'l1tOmtfEventPrint', 'l1MuonAnalyzerOmtf'), #'l1tOmtfEventPrint', 'l1MuonAnalyzerOmtf'
       omtfEventPrint = cms.untracked.PSet(    
                         filename  = cms.untracked.string(outFilesName),
                         extension = cms.untracked.string('.txt'),                
                         threshold = cms.untracked.string("DEBUG"), #DEBUG
                         default = cms.untracked.PSet( limit = cms.untracked.int32(0) ), 
                         #INFO   =  cms.untracked.int32(0),
                         #DEBUG   = cms.untracked.int32(0),
                         l1tOmtfEventPrint = cms.untracked.PSet( limit = cms.untracked.int32(1000000000) ),
                         OMTFReconstruction = cms.untracked.PSet( limit = cms.untracked.int32(1000000000) ),
                         l1MuonAnalyzerOmtf = cms.untracked.PSet( limit = cms.untracked.int32(1000000000) ),
                       ),
       debugModules = cms.untracked.vstring('L1MuonAnalyzerOmtf', 'simOmtfPhase2Digis', 'omtfParamsSource', 'omtfParams', "esProd", 'L1TMuonOverlapPhase1ParamsESProducer') #'L1MuonAnalyzerOmtf',
       #debugModules = cms.untracked.vstring('*')
    )
    
if not options.verbose:
    process.MessageLogger.cerr.FwkReport.reportEvery = cms.untracked.int32(1000)
    process.options = cms.untracked.PSet(wantSummary = cms.untracked.bool(False), 
                                         #SkipEvent = cms.untracked.vstring('ProductNotFound') 
                                     )
    
    
# PostLS1 geometry used
process.load('Configuration.Geometry.GeometryExtended2026D86Reco_cff')
process.load('Configuration.Geometry.GeometryExtended2026D86_cff') 
############################
#process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')
#from Configuration.AlCa.GlobalTag_condDBv2 import GlobalTag
#process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_mc', '')    
    
    
# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
#process.load('Configuration.Geometry.GeometryExtended2026D41Reco_cff')
#process.load('Configuration.Geometry.GeometryExtended2026D41_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
#process.load('Configuration.StandardSequences.SimL1Emulator_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

from Configuration.AlCa.GlobalTag import GlobalTag
#process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:upgradePLS3', '')
process.GlobalTag = GlobalTag(process.GlobalTag, '103X_upgrade2023_realistic_v2', '') 

firstEv = 0#40000
#nEvents = 1000

# input files (up to 255 files accepted)
process.source = cms.Source('PoolSource',
fileNames = cms.untracked.vstring( 
    #'file:/eos/user/k/kbunkow/cms_data/SingleMuFullEta/721_FullEta_v4/SingleMu_16_p_1_1_xTE.root',
    #'file:/afs/cern.ch/user/k/kpijanow/Neutrino_Pt-2to20_gun_50.root',
    options.inputFiles ),
    skipEvents =  cms.untracked.uint32(0),
    inputCommands=cms.untracked.vstring(
        'keep *',
        'drop l1tEMTFHit2016Extras_simEmtfDigis_CSC_HLT',
        'drop l1tEMTFHit2016Extras_simEmtfDigis_RPC_HLT',
        'drop l1tEMTFHit2016s_simEmtfDigis__HLT',
        'drop l1tEMTFTrack2016Extras_simEmtfDigis__HLT',
        'drop l1tEMTFTrack2016s_simEmtfDigis__HLT')
)

# Calibrate Digis
process.load("L1Trigger.DTTriggerPhase2.CalibratedDigis_cfi")
process.CalibratedDigis.dtDigiTag = "simMuonDTDigis" 
process.CalibratedDigis.scenario = 0

# DTTriggerPhase2
process.load("L1Trigger.DTTriggerPhase2.dtTriggerPhase2PrimitiveDigis_cfi")
process.dtTriggerPhase2PrimitiveDigis.scenario = 0

####Event Setup Producer
process.load('L1Trigger.L1TMuonOverlapPhase1.fakeOmtfParams_cff')
process.omtfParams.configXMLFile = cms.FileInPath("L1Trigger/L1TMuon/data/omtf_config/hwToLogicLayer_0x0209.xml")
process.omtfParams.patternsXMLFiles = cms.VPSet(
        cms.PSet(patternsXMLFile=cms.FileInPath("L1Trigger/L1TMuon/data/omtf_config/Patterns_ExtraplMB1nadMB2DTQualAndEtaFixedP_ValueP1Scale_t20_v1_SingleMu_iPt_and_OneOverPt_classProb17_recalib2_minDP0.xml")),)

process.esProd = cms.EDAnalyzer("EventSetupRecordDataGetter",
   toGet=cms.VPSet(
      cms.PSet(record=cms.string('L1TMuonOverlapParamsRcd'),
               data=cms.vstring('L1TMuonOverlapParams'))
                   ),
   verbose=cms.untracked.bool(False)
)

process.TFileService = cms.Service("TFileService", fileName = cms.string(outFilesName + '.root'), closeFileFast = cms.untracked.bool(True) )
                                   
####OMTF Emulator
if options.useExtrapolationAlgo :
    process.load('L1Trigger.L1TMuonOverlapPhase2.simOmtfPhase2Digis_extrapol_cfi')
else :
    process.load('L1Trigger.L1TMuonOverlapPhase2.simOmtfPhase2Digis_cfi')

process.simOmtfPhase2Digis.dumpResultToXML = cms.bool(False)
process.simOmtfPhase2Digis.XMLDumpFileName = cms.string(outFilesName + ".xml")

#needed only for the hits dumper
process.simOmtfPhase2Digis.dumpHitsToROOT = cms.bool(options.dump)
process.simOmtfPhase2Digis.candidateSimMuonMatcher = cms.bool(options.dump)
if (options.matchUsingPropagator):
    process.simOmtfPhase2Digis.candidateSimMuonMatcherType = cms.string("propagation")
else: 
    process.simOmtfPhase2Digis.candidateSimMuonMatcherType = cms.string("matchSimple")


if (options.dump):
    process.simOmtfPhase2Digis.simTracksTag = cms.InputTag('g4SimHits')
    process.simOmtfPhase2Digis.simVertexesTag = cms.InputTag('g4SimHits')
    process.simOmtfPhase2Digis.muonMatcherFile = cms.FileInPath("L1Trigger/L1TMuon/data/omtf_config/muonMatcherHists_100files_smoothStdDev_withOvf.root")
if options.useExtrapolationAlgo :
    process.simOmtfPhase2Digis.patternsXMLFile = cms.FileInPath("L1Trigger/L1TMuon/data/omtf_config/Patterns_ExtraplMB1nadMB2DTQualAndEtaFixedP_ValueP1Scale_t20_v1_SingleMu_iPt_and_OneOverPt_classProb17_recalib2_minDP0.xml")
else :
    process.simOmtfPhase2Digis.patternsXMLFile = cms.FileInPath("L1Trigger/L1TMuon/data/omtf_config/Patterns_0x00012_oldSample_3_30Files_grouped1_classProb17_recalib2.xml") ##todo

  
process.simOmtfPhase2Digis.rpcMaxClusterSize = cms.int32(3)
process.simOmtfPhase2Digis.rpcMaxClusterCnt = cms.int32(2)
process.simOmtfPhase2Digis.rpcDropAllClustersIfMoreThanMax = cms.bool(True)


process.simOmtfPhase2Digis.noHitValueInPdf = cms.bool(True)

process.simOmtfPhase2Digis.lctCentralBx = cms.int32(8);# if the data were generated with the previous CMSSW_10_X then you have to use 6

if options.useExtrapolationAlgo :
    process.simOmtfPhase2Digis.dtRefHitMinQuality =  cms.int32(4)

    process.simOmtfPhase2Digis.usePhiBExtrapolationFromMB1 = cms.bool(True)
    process.simOmtfPhase2Digis.usePhiBExtrapolationFromMB2 = cms.bool(True)
    
    #process.simOmtfPhase2Digis.goldenPatternResultFinalizeFunction = cms.int32(10) #valid values are 0, 1, 2, 3, 5
    
    process.simOmtfPhase2Digis.minDtPhiQuality = cms.int32(options.minDtPhiQuality)
    process.simOmtfPhase2Digis.minDtPhiBQuality = cms.int32(options.minDtPhiBQuality) #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<!!!!!!!!!!!!!!!!!!
    
    #process.simOmtfPhase2Digis.useEndcapStubsRInExtr  = cms.bool(True)   #TODO REMOVE <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    #process.simOmtfPhase2Digis.useFloatingPointExtrapolation  = cms.bool(False)
    #process.simOmtfPhase2Digis.extrapolFactorsFilename = cms.FileInPath("L1Trigger/L1TMuon/data/omtf_config/ExtrapolationFactors_withQAndEta.xml")
else :
    process.simOmtfPhase2Digis.minDtPhiQuality = cms.int32(options.minDtPhiQuality)
    process.simOmtfPhase2Digis.minDtPhiBQuality = cms.int32(options.minDtPhiBQuality) #in 2023 it was 2, but 4 reduces the rate  #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<!!!!!!!!!!!!!!!!!!
         

if options.useNN:
    process.simOmtfPhase2Digis.neuralNetworkFile = cms.FileInPath("L1Trigger/L1TMuon/data/omtf_config/lutNN_omtfRegression_FP_v217.xml")


#process.dumpED = cms.EDAnalyzer("EventContentAnalyzer")
#process.dumpES = cms.EDAnalyzer("PrintEventSetupContent")

#process.load("Configuration.StandardSequences.GeometryRecoDB_cff")
#process.load("Configuration.StandardSequences.MagneticField_38T_cff")

process.load("TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorAlong_cfi")
#process.load("TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorOpposite_cfi")
#process.load("TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorAny_cfi")


process.L1TMuonSeq = cms.Sequence( process.esProd          
                                   + process.simOmtfPhase2Digis 
                                   #+ process.dumpED
                                   #+ process.dumpES
)

#process.L1TMuonPath = cms.Path(process.L1TMuonSeq) ########################################<<<<<<!!!!!!!!!!!!!!!!!!!!!!!!!!!
process.L1TMuonPath = cms.Path(process.CalibratedDigis *
                               process.dtTriggerPhase2PrimitiveDigis * 
                               process.L1TMuonSeq)

process.schedule = cms.Schedule(process.L1TMuonPath)

process.out = cms.OutputModule("PoolOutputModule", 
                               fileName = cms.untracked.string(options.outputFile),
                               fastCloning = cms.untracked.bool( False ),
                               dataset = cms.untracked.PSet(
                                   dataTier = cms.untracked.string( 'RECO' ),
                                   filterName = cms.untracked.string( '' )
                               ),
                               outputCommands = cms.untracked.vstring("drop *",
                                                                      "keep recoGenParticles_*_*_*",
                                                                      "keep *_genParticles_*_*",
                                                                      "keep l1tRegionalMuonCandBXVector_*_OMTF_*",
                                                                      "keep SimTracks_*_*_*",
                                                                      "keep SimVertexs_*_*_*",
                                                                      "keep *_dispGen_*_*")
                           )

#)

process.output_step = cms.EndPath(process.out)
#process.schedule = cms.Schedule(process.L1TMuonPath)
process.schedule.extend([process.output_step])
