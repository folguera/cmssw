#!/usr/bin/env python
import os, re
import math, time

print ('START')

########   YOU ONLY NEED TO FILL THE AREA BELOW   #########
########   customization  area #########
NumberOfJobs= 250 # number of jobs to be submitted
interval = 2 # number files to be processed in a single job, take care to split your file so that you run on all files. The last job might be with smaller number of files (the ones that remain).
OutputFileNames = "l1omtf" # base of the output file name, they will be saved in res directory
#ScriptName = "runMuonOverlap_SF_wNN.py" # script to be used with cmsRun
ScriptName = "runMuonOverlap_SF.py" # script to be used with cmsRun
FileList = "list_MuonGunSample_Pt1to1000_106X.txt"
#FileList = "list_SingleMu_FlatPt1to1000_FullEta_125X.txt"
#FileList = "list_SingleMu_OneOverPt_FullEta.txt" #] # list with all the file directories
#FileList = "list_DY.txt" # list with all the file directories
queue = "workday" # give bsub queue -- 8nm (8 minutes), 1nh (1 hour), 8nh, 1nd (1day), 2nd, 1nw (1 week), 2nw 
OutputDir = ["/eos/cms/store/user/folguera/L1TMuon/OMTF/2023_03_UsePhase2DTs_NewPats_t11/noP2DTs/",
             "/eos/cms/store/user/folguera/L1TMuon/OMTF/2023_03_UsePhase2DTs_NewPats_t11/withP2DTs/",
             "/eos/cms/store/user/folguera/L1TMuon/OMTF/2023_03_UsePhase2DTs_NewPats_t11/withP2DTs_minLay2/",
             "/eos/cms/store/user/folguera/L1TMuon/OMTF/2023_03_UsePhase2DTs_NewPats_t11/withP2DTsHQ/",
             "/eos/cms/store/user/folguera/L1TMuon/OMTF/2023_03_UsePhase2DTs_NewPats_t11/noRPCs/",
             "/eos/cms/store/user/folguera/L1TMuon/OMTF/2023_03_UsePhase2DTs_NewPats_t11/noRPCs_minLay2/"]
customize = ["usePhase2DTs=False", 
             "usePhase2DTs=True",
             "usePhase2DTs=True minFiredLayers=2",
             "usePhase2DTs=True minDtPhiQuality=4 minDtPhiBQuality=5",
             "usePhase2DTs=True dropRPCs=True",
             "usePhase2DTs=True dropRPCs=True minFiredLayers=2"] 

### dropRPCs = "dropRPCs=False "
### useNN = "useNN=False "
### minDTQuality="minDtPhiQuality=2 "
### minDTbQuality="minDtPhiBQuality=4 "
########   customization end   #########
print ('do not worry about folder creation:')
os.system("rm -rf tmp")
os.system("rm -rf exec")
os.system("mkdir tmp")
os.system("mkdir exec")

for i in range(len(customize)):
    print(i)
    OutDir = OutputDir[i]
    if "MuonGunSample" in FileList: 
        OutDir += "MuonGunSample_Pt1to1000_106X/"
    elif "SingleMu_OneOverPt" in FileList:
        OutDir += "SingleMu_OneOverPt_FullEta_125X/"
    elif "SingleMu_FlatPt1to1000_FullEta_125X":
        OutDir += "SingleMu_FlatPt1to1000_FullEta_125X/"

    path = os.getcwd()
    print ("runnning: " + customize[i])
    print ("saving tuples in: " +OutDir )
    print ("reading tuples from: "+FileList)
    os.system("mkdir %s/%s" %(OutDir,int(time.time())))

    ##### loop for creating and sending jobs #####
    for x in range(1, int(NumberOfJobs)+1):
        ##### creates directory and file list for job #######
        os.system("sed '"+str(1+interval*(x-1))+","+str(interval*x)+"!d' "+FileList+" > tmp/list_"+str(x)+".txt ")
        
        ##### creates jobs #######
        with open('exec/job_'+str(NumberOfJobs*i+x)+'.sh', 'w') as fout:
            fout.write("#!/bin/sh\n")
            fout.write("echo\n")
            fout.write("echo\n")
            fout.write("echo 'START---------------'\n")
            fout.write("echo 'WORKDIR ' ${PWD}\n")
            fout.write("cd "+str(path)+"\n")
            fout.write("eval `scramv1 runtime -sh`\n")
            fout.write("export X509_USER_PROXY=$1\n")
            fout.write("voms-proxy-info -all\n")
            fout.write("voms-proxy-info -all -file $1\n")
            fout.write("cmsRun "+ScriptName+" outputFile='"+OutDir+OutputFileNames+"_"+str(x)+".root' inputFiles_clear inputFiles_load='tmp/list_"+str(x)+".txt' "+customize[i]+"\n")
            fout.write("echo 'STOP---------------'\n")
            fout.write("echo\n")
            fout.write("echo\n")
            os.system("chmod 755 exec/job_"+str(NumberOfJobs*i+x)+".sh")
            
###### create submit.sub file ####
with open('submit.sub', 'w') as fout:
    fout.write("executable              = $(filename)\n")
    fout.write("arguments               = $(ClusterId)$(ProcId)\n")
    fout.write("output                  = batchlogs/$(ClusterId).$(ProcId).out\n")
    fout.write("error                   = batchlogs/$(ClusterId).$(ProcId).err\n")
    fout.write("log                     = batchlogs/$(ClusterId).log\n")
    fout.write('+JobFlavour = "%s"\n' %(queue))
    fout.write("\n")
    fout.write('Proxy_path=/afs/cern.ch/user/f/folguera/workdir/proxy/x509up_u50826\n')
    fout.write('arguments               = $(Proxy_path) arg2 arg3 arg4\n')
    fout.write("\n")
    fout.write("queue filename matching (exec/job_*sh)\n")
    
###### sends bjobs ######
os.system("echo submit.sub")
os.system("condor_submit submit.sub")
print()
   
print()
print( "your jobs:")
os.system("condor_q")
print()
print()
