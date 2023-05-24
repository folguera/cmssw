# -*- coding: utf-8 -*-
import FWCore.ParameterSet.Config as cms
import os
import sys

import FWCore.ParameterSet.VarParsing as VarParsing


# setup any defaults you want
options = VarParsing.VarParsing( 'analysis' )

options.register('usePhase2DTs',
                 False, # default value
                 VarParsing.VarParsing.multiplicity.singleton, # singleton or list
                 VarParsing.VarParsing.varType.bool,            # string, int, or float
                 "use Phase2 TPs")

options.register('dropRPCs',
                 False, # default value
                 VarParsing.VarParsing.multiplicity.singleton, # singleton or list
                 VarParsing.VarParsing.varType.bool,            # string, int, or float
                 "Drop RPC TPs")

options.register('verbose',
                 False,
                 VarParsing.VarParsing.multiplicity.singleton, # singleton or list
                 VarParsing.VarParsing.varType.bool,            # string, int, or float
                 "Activate Verbosity")

options.register('dump',
                 False,
                 VarParsing.VarParsing.multiplicity.singleton, # singleton or list
                 VarParsing.VarParsing.varType.bool,            # string, int, or float
                 "Activate dump")

options.register('useNN',
                 False,
                 VarParsing.VarParsing.multiplicity.singleton, # singleton or list
                 VarParsing.VarParsing.varType.bool,            # string, int, or float
                 "Use NN for momentum assignment")

options.register('minDtPhiQuality',
                 2,
                 VarParsing.VarParsing.multiplicity.singleton, # singleton or list
                 VarParsing.VarParsing.varType.int,
                 "Min DT phi quality")

options.register('minDtPhiBQuality',
                 4,
                 VarParsing.VarParsing.multiplicity.singleton, # singleton or list
                 VarParsing.VarParsing.varType.int,
                 "Min DT phi quality")

options.register('minFiredLayers',
                 3,
                 VarParsing.VarParsing.multiplicity.singleton, # singleton or list
                 VarParsing.VarParsing.varType.int,
                 "MinFiredLayers")
                 
###options.register('outputFile',
###                 'l1omts.root',
###                 VarParsing.VarParsing.multiplicity.singleton, # singleton or list
###                 VarParsing.VarParsing.varType.string,            # string, int, or float
###                 "output filename")
###
###options.register('inputFiles',
###                 'file:/eos/cms/store/user/folguera/OMTF/MuonGunSample_106X/MuonFlatPt1to1000_1001_numEvent2000.root',
###                 VarParsing.VarParsing.multiplicity.list, # singleton or list
###                 VarParsing.VarParsing.varType.string,    # string, int, or float
###                 "input filename")

options.outputFile = 'l1tomtf.root'
#options.inputFiles = 'file:/eos/cms/store/user/folguera/OMTF/MuonGunSample_106X/MuonFlatPt1to1000_1001_numEvent2000.root'
options.inputFiles = 'file:///eos/user/a/akalinow/Data/SingleMu/12_5_2_p1_15_02_2023/SingleMu_ch0_iPt0_12_5_2_p1_15_02_2023/12_5_2_p1_15_02_2023/230216_100233/0000/SingleMu_iPt_0_m_16.root'

# get and parse the command line arguments
options.parseArguments()


process = cms.Process("L1TMuonEmulation")
process.load("FWCore.MessageLogger.MessageLogger_cfi")


if options.verbose : 
    
    filenameverbose = "log_MuonOverlap"
    if options.usePhase2DTs: 
        filenameverbose += "_Phase2"

    process.MessageLogger = cms.Service("MessageLogger",
       #suppressInfo       = cms.untracked.vstring('AfterSource', 'PostModule'),
       destinations   = cms.untracked.vstring(
                                               #'detailedInfo',
                                               #'critical',
                                               #'cout',
                                               #'cerr',
                                               'omtfEventPrint'
                    ),
       categories        = cms.untracked.vstring('l1tOmtfEventPrint', 'OMTFReconstruction'),
       omtfEventPrint = cms.untracked.PSet(    
                         filename  = cms.untracked.string(filenameverbose),
                         extension = cms.untracked.string('.txt'),                
                         threshold = cms.untracked.string('DEBUG'),
                         default = cms.untracked.PSet( limit = cms.untracked.int32(0) ), 
                         #INFO   =  cms.untracked.int32(0),
                         #DEBUG   = cms.untracked.int32(0),
                         l1tOmtfEventPrint = cms.untracked.PSet( limit = cms.untracked.int32(1000000000) ),
                         OMTFReconstruction = cms.untracked.PSet( limit = cms.untracked.int32(1000000000) )
                       ),
       debugModules = cms.untracked.vstring('L1MuonAnalyzerOmtf', 'simOmtfPhase2Digis') 
       #debugModules = cms.untracked.vstring('*')
    )

    #process.MessageLogger.cerr.FwkReport.reportEvery = cms.untracked.int32(100)
if not options.verbose:
    process.MessageLogger.cerr.FwkReport.reportEvery = cms.untracked.int32(1000)
    process.options = cms.untracked.PSet(wantSummary = cms.untracked.bool(False), 
                                         #SkipEvent = cms.untracked.vstring('ProductNotFound') 
                                     )
# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.Geometry.GeometryExtended2026D49Reco_cff')
process.load('Configuration.Geometry.GeometryExtended2026D49_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
#process.load('Configuration.StandardSequences.SimL1Emulator_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')

## Global tag
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:phase2_realistic_T15', '')

process.source = cms.Source('PoolSource',

 fileNames = cms.untracked.vstring(
     options.inputFiles
 ),
 
        inputCommands=cms.untracked.vstring(
        'keep *',
        'drop l1tEMTFHit2016Extras_simEmtfDigis_CSC_HLT',
        'drop l1tEMTFHit2016Extras_simEmtfDigis_RPC_HLT',
        'drop l1tEMTFHit2016s_simEmtfDigis__HLT',
        'drop l1tEMTFTrack2016Extras_simEmtfDigis__HLT',
        'drop l1tEMTFTrack2016s_simEmtfDigis__HLT')
)
	                    
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1))


####Event Setup Producer
process.load('L1Trigger.L1TMuonOverlapPhase1.fakeOmtfParams_cff')
process.omtfParams.configXMLFile = cms.FileInPath("L1Trigger/L1TMuon/data/omtf_config/hwToLogicLayer_0x0008.xml")

process.esProd = cms.EDAnalyzer("EventSetupRecordDataGetter",
   toGet = cms.VPSet(
      cms.PSet(record = cms.string('L1TMuonOverlapParamsRcd'),
               data = cms.vstring('L1TMuonOverlapParams'))
                   ),
   verbose = cms.untracked.bool(False)
)

#process.TFileService = cms.Service("TFileService", fileName = cms.string('omtfAnalysis2_74_nuGun_PU250_' + analysisType + '.root'), closeFileFast = cms.untracked.bool(True) )
#process.TFileService = cms.Service("TFileService", fileName = cms.string('SingleMu_PU200_' + analysisType + '_t100.root'), closeFileFast = cms.untracked.bool(True) )
 
                                   
####OMTF Emulator
process.load('L1Trigger.L1TMuonOverlapPhase2.simOmtfPhase2Digis_cfi')

process.simOmtfPhase2Digis.dumpResultToXML = cms.bool(options.dump)
process.simOmtfPhase2Digis.dumpResultToROOT = cms.bool(options.dump)
process.simOmtfPhase2Digis.eventCaptureDebug = cms.bool(options.dump)


#rocess.simOmtfPhase2Digis.patternsXMLFile = cms.FileInPath("L1Trigger/L1TMuon/data/omtf_config/Patterns_0x00012_oldSample_3_30Files_grouped1_classProb17_recalib2.xml")
#process.simOmtfPhase2Digis.patternsXMLFile = cms.FileInPath("L1Trigger/L1TMuon/data/omtf_config/Patterns_0x0009_oldSample_3_10Files.xml")
#process.simOmtfPhase2Digis.patternsXMLFile = cms.FileInPath("L1Trigger/L1TMuon/data/omtf_config/Patterns_0x0003.xml")
#process.simOmtfPhase2Digis.patternsXMLFiles = cms.VPSet(cms.PSet(patternsXMLFile = cms.FileInPath("GPs_parametrised_plus_v1.xml")),
#                                                       cms.PSet(patternsXMLFile = cms.FileInPath("L1Trigger/L1TMuon/data/omtf_config/GPs_parametrised_minus_v1.xml"))
#)

process.simOmtfPhase2Digis.sorterType = cms.string("byLLH")


####  CUSTOMIZATION
process.simOmtfPhase2Digis.dropDTPrimitives = cms.bool(options.usePhase2DTs)  
process.simOmtfPhase2Digis.usePhase2DTPrimitives = cms.bool(options.usePhase2DTs) #if here is true, dropDTPrimitives should also be true
process.simOmtfPhase2Digis.minDtPhiQuality = cms.int32(options.minDtPhiQuality)
process.simOmtfPhase2Digis.minDtPhiBQuality = cms.int32(options.minDtPhiBQuality)
process.simOmtfPhase2Digis.minFiredLayers = cms.int32(options.minFiredLayers)

if options.usePhase2DTs: 
    process.simOmtfPhase2Digis.patternsXMLFile = cms.FileInPath("L1Trigger/L1TMuon/data/omtf_config/Patterns_layerStat_t11_Phase2DTs_classProb.xml")
else: 
    process.simOmtfPhase2Digis.patternsXMLFile = cms.FileInPath("L1Trigger/L1TMuon/data/omtf_config/Patterns_layerStat_t11_classProb.xml")

process.simOmtfPhase2Digis.rpcMaxClusterSize = cms.int32(3)
process.simOmtfPhase2Digis.rpcMaxClusterCnt = cms.int32(2)
process.simOmtfPhase2Digis.rpcDropAllClustersIfMoreThanMax = cms.bool(True)

process.simOmtfPhase2Digis.dropRPCPrimitives= cms.bool(options.dropRPCs)

process.simOmtfPhase2Digis.goldenPatternResultFinalizeFunction = cms.int32(9) #valid values are 0, 1, 2, 3, 5

process.simOmtfPhase2Digis.noHitValueInPdf = cms.bool(True)

process.simOmtfPhase2Digis.lctCentralBx = cms.int32(8);#<<<<<<<<<<<<<<<<!!!!!!!!!!!!!!!!!!!!TODO this was changed in CMSSW 10(?) to 8. if the data were generated with the previous CMSSW then you have to use 6




#nn_pThresholds = [0.36, 0.38, 0.40, 0.42, 0.44, 0.46, 0.48, 0.50, 0.52, 0.54 ]
#nn_pThresholds = [0.40, 0.50] 
nn_pThresholds = [0.35, 0.40, 0.45, 0.50, 0.55] 

if (options.useNN):
    process.simOmtfPhase2Digis.neuralNetworkFile = cms.FileInPath("L1Trigger/L1TMuon/data/omtf_config/omtfClassifier_withPtBins_v34.txt")
    process.simOmtfPhase2Digis.ptCalibrationFileName = cms.FileInPath("L1Trigger/L1TMuon/data/omtf_config/PtCalibration_v34.root")
    process.simOmtfPhase2Digis.nn_pThresholds = cms.vdouble(nn_pThresholds)


#process.dumpED = cms.EDAnalyzer("EventContentAnalyzer")
#process.dumpES = cms.EDAnalyzer("PrintEventSetupContent")

#process.load("Configuration.StandardSequences.GeometryRecoDB_cff")
#process.load("Configuration.StandardSequences.MagneticField_38T_cff")

process.load("TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorAlong_cfi")
#process.load("TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorOpposite_cfi")
#process.load("TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorAny_cfi")


#process.l1MuonAnalyzerOmtfPath = cms.Path(process.L1MuonAnalyzerOmtf)

                                          
if options.usePhase2DTs:
    process.load("L1Trigger.DTTriggerPhase2.CalibratedDigis_cfi")
    process.CalibratedDigis.dtDigiTag = "simMuonDTDigis"
    
    process.load("L1Trigger.DTTriggerPhase2.dtTriggerPhase2PrimitiveDigis_cfi")
    process.dtTriggerPhase2PrimitiveDigis.scenario = 1 #0 is mc, 1 is data, 2 is slice test

    
    process.L1TMuonSeq = cms.Sequence( process.esProd               
                                       + process.CalibratedDigis
                                       + process.dtTriggerPhase2PrimitiveDigis
                                       + process.simOmtfPhase2Digis 
                                   )
    
else: 
    process.L1TMuonSeq = cms.Sequence( process.esProd                                          
                                       + process.simOmtfPhase2Digis 
                                       #+ process.dumpED
                                       #+ process.dumpES
                                   )

process.L1TMuonPath = cms.Path(process.L1TMuonSeq)

#process.load("L1Trigger.TrackFindingTracklet.L1TrackletTracks_cff")
#process.TTTracks = cms.Path(process.L1TrackletTracks)
#process.TTTracksWithTruth = cms.Path(process.L1TrackletTracksWithAssociators)

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
                                                                      "keep SimVertexs_*_*_*")
                           )

#)

process.output_step = cms.EndPath(process.out)
#process.schedule = cms.Schedule(process.L1TMuonPath)
process.schedule.extend([process.output_step])
