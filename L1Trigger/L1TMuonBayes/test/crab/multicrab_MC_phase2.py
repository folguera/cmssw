from WMCore.Configuration import Configuration
from CRABClient.UserUtilities import config, getUsernameFromSiteDB
config = Configuration()

config.section_('General')
config.General.transferOutputs = True
config.General.workArea = 'crab_projects_P2TP_v2/'

config.section_('JobType')
config.JobType.psetName = '../runMuonOverlap.py'
config.JobType.pluginName = 'Analysis'
config.JobType.outputFiles = ['l1tomtf.root']
config.JobType.pyCfgParams = ['doPhase2TPs=True']
config.JobType.allowUndistributedCMSSW = True

config.section_('Data')
config.Data.splitting = 'FileBased'
config.JobType.maxMemoryMB = 2500
config.Data.outLFNDirBase = '/store/user/folguera/OMTF/Feb20_P2TP_v2/'
config.Data.publication = False

config.section_('Site')
config.Site.storageSite = 'T2_CH_CERN'

if __name__ == '__main__':

    from CRABAPI.RawCommand import crabCommand
    from CRABClient.ClientExceptions import ClientException
    from httplib import HTTPException
    from multiprocessing import Process

    def submit(config):
        try:
            crabCommand('submit', config = config)
        except HTTPException as hte:
            print "Failed submitting task: %s" % (hte.headers)
        except ClientException as cle:
            print "Failed submitting task: %s" % (cle)

    #############################################################################################
    ## From now on that's what users should modify: this is the a-la-CRAB2 configuration part. ##
    #############################################################################################
    #############################################################################    
    MUONGUN=True
    NUGUN=True
    DISPLACED=False

    #### Muon Guns
    if MUONGUN:
        config.General.requestName = 'L1MuPhase2Ntuples_Mu_FlatPt2to100_PU200'    
        config.Data.unitsPerJob = 5 #180 #minutes
        config.Data.inputDataset = '/Mu_FlatPt2to100-pythia8-gun/PhaseIITDRSpring19DR-PU200_106X_upgrade2023_realistic_v3-v2/GEN-SIM-DIGI-RAW'
        p = Process(target=submit, args=(config,))
        p.start()
        p.join()

    #### Nu Guns
    if NUGUN:
        config.General.requestName = 'L1MuPhase2Ntuples_Nu_E10_PU200'    
        config.Data.unitsPerJob = 5 #180 #minutes
        config.Data.inputDataset = '/Nu_E10-pythia8-gun/PhaseIITDRSpring19DR-PU200_106X_upgrade2023_realistic_v3-v3/GEN-SIM-DIGI-RAW'
        p = Process(target=submit, args=(config,))
        p.start()
        p.join()

##SF        config.General.requestName = 'L1MuPhase2Ntuples_Nu_E10_PU140'    
##SF        config.Data.unitsPerJob = 2
##SF        config.Data.inputDataset = '/Nu_E10-pythia8-gun/PhaseIITDRSpring19DR-PU140_106X_upgrade2023_realistic_v3_ext3-v1/GEN-SIM-DIGI-RAW'
##SF        p = Process(target=submit, args=(config,))
##SF        p.start()
##SF        p.join()
##SF
##SF        config.General.requestName = 'L1MuPhase2Ntuples_Nu_E10_PU250'
##SF        config.Data.unitsPerJob = 2
##SF        config.Data.inputDataset = '/Nu_E10-pythia8-gun/PhaseIITDRSpring19DR-PU250_106X_upgrade2023_realistic_v3_ext2-v1/GEN-SIM-DIGI-RAW'
##SF        p = Process(target=submit, args=(config,))
##SF        p.start()
##SF        p.join()
##SF


    #### DISPLACED MUON Guns
    if DISPLACED:
        config.General.requestName = 'L1MuPhase2Ntuples_DisplacedMuonGun_Pt30To100_Dxy_0_1000'
        config.Data.unitsPerJob = 5
        config.Data.inputDataset = '/DisplacedMuons_Pt30to100_Dxy0to3000-pythia8-gun/PhaseIITDRSpring19DR-PU200_106X_upgrade2023_realistic_v3-v1/GEN-SIM-DIGI-RAW'
        p = Process(target=submit, args=(config,))
        p.start()
        p.join()
        
        config.General.requestName = 'L1MuPhase2Ntuples_DisplacedMuonGun_Pt2To10_Dxy_0_1000'
        config.Data.unitsPerJob = 5
        config.Data.inputDataset = '/DisplacedMuons_Pt2to10_Dxy0to3000-pythia8-gun/PhaseIITDRSpring19DR-PU200_106X_upgrade2023_realistic_v3-v1/GEN-SIM-DIGI-RAW'
        p = Process(target=submit, args=(config,))
        p.start()
        p.join()
        
        config.General.requestName = 'L1MuPhase2Ntuples_DisplacedMuonGun_Pt10To30_Dxy_0_1000'
        config.Data.unitsPerJob = 5
        config.Data.inputDataset = '/DisplacedMuons_Pt10to30_Dxy0to3000-pythia8-gun/PhaseIITDRSpring19DR-PU200_106X_upgrade2023_realistic_v3-v1/GEN-SIM-DIGI-RAW'
        p = Process(target=submit, args=(config,))
        p.start()
        p.join()








