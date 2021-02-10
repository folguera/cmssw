from CRABClient.UserUtilities import config #, getUsernameFromSiteDB
config = config()

#type = 'omtf_nn'
type = 'omtf_0x0006'

config.General.requestName = type + '_MC_analysis_MuFlatPt_PU200_v3_t100'
#config.General.workArea = 'crab_projects'
config.General.transferOutputs = True
config.General.transferLogs = True

config.JobType.pluginName = 'Analysis'
#config.JobType.psetName = 'runMuonOverlapTTMergerAnalyzerCrab.py'

if type == 'omtf_nn' :
    config.JobType.psetName = 'runMuonOverlap_nn_phase2.py'
else :
    config.JobType.psetName = 'runMuonOverlap_0x0006.py'

config.JobType.pyCfgParams = ['efficiency']

config.Data.inputDataset = '/Mu_FlatPt2to100-pythia8-gun/PhaseIITDRSpring19DR-PU200_106X_upgrade2023_realistic_v3-v2/GEN-SIM-DIGI-RAW' 
#'/SingleMu_FlatPt-2to100/PhaseIIFall17D-L1TPU200_93X_upgrade2023_realistic_v5-v1/GEN-SIM-DIGI-RAW'
#config.Data.inputDataset = '/SingleMu_FlatPt-2to100/PhaseIIFall17D-L1TnoPU_93X_upgrade2023_realistic_v5-v1/GEN-SIM-DIGI-RAW'

config.Data.inputDBS = 'global'
config.Data.splitting = 'FileBased'
config.Data.unitsPerJob = 5
#config.Data.outLFNDirBase = '/store/user/%s/' % (getUsernameFromSiteDB())
config.Data.publication = False
config.Data.outputDatasetTag = 'CRAB3_' + type + 'omtf_nn_MC_analysis_MuFlatPt_PU200_v3_t100'
config.Data.totalUnits = 321
config.Data.ignoreLocality = False

config.section_("Debug")
config.Debug.extraJDL = ['+CMS_ALLOW_OVERFLOW=False']

#config.Site.storageSite = 'T2_PL_Swierk'
config.Site.storageSite = 'T2_CH_CERN'

