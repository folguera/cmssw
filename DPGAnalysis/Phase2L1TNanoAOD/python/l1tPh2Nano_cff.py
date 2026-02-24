import FWCore.ParameterSet.Config as cms
from PhysicsTools.NanoAOD.nano_cff import nanoMetadata
from DPGAnalysis.Phase2L1TNanoAOD.l1tPh2MuNanotables_cff import *

l1tPh2NanoTask = cms.Task(nanoMetadata)
l1tPh2NanoSequence = cms.Sequence(l1tPh2NanoTask)

### P2GT objects
from DPGAnalysis.Phase2L1TNanoAOD.l1tPh2GTtables_cff import *
def addPh2GTObjects(process):
    process.l1tPh2NanoTask.add(p2GTL1TablesTask)
    return process

### Main Ph2L1 objects
from DPGAnalysis.Phase2L1TNanoAOD.l1tPh2Nanotables_cff import *
def addPh2L1Objects(process):
    process.l1tPh2NanoTask.add(p2L1TablesTask)
    return process

#### GENERATOR INFO
## based on https://github.com/cms-sw/cmssw/blob/master/PhysicsTools/NanoAOD/python/nanogen_cff.py#L2-L36
from PhysicsTools.NanoAOD.genparticles_cff import * ## for GenParts
from PhysicsTools.NanoAOD.jetMC_cff import * ## for GenJets
from PhysicsTools.NanoAOD.met_cff import metMCTable ## for GenMET
from PhysicsTools.NanoAOD.globals_cff import puTable ## for PU
from PhysicsTools.NanoAOD.taus_cff import * ## for Gen taus
def addGenObjects(process):
    process.load("TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagator_cfi")
    
    ## add more GenVariables
    # from L1Ntuple Gen: https://github.com/artlbv/cmssw/blob/94a5ec13b8ce76afb8ea4f157bb92fb547fadee2/L1Trigger/L1TNtuples/plugins/L1GenTreeProducer.cc#L203
    genParticleTable.variables.vertX = Var("vertex.x", float, "vertex X")
    genParticleTable.variables.vertY = Var("vertex.y", float, "vertex Y")
    genParticleTable.variables.vertZ = Var("vertex.z", float, "vertex Z")
    genParticleTable.variables.lXY = Var("sqrt(vertex().x() * vertex().x() + vertex().y() * vertex().y())", float, "lXY")
    genParticleTable.variables.dXY = Var("-vertex().x() * sin(phi()) + vertex().y() * cos(phi())", float, "dXY")
    
    ## Producer de propagación a estaciones de muones (comentado)
    process.genParticlePropagator = cms.EDProducer("GenParticlePropagator",
        src = cms.InputTag("finalGenParticles"),
        # Muon track extrapolation to 1st station
        muProp1st = cms.PSet(
            useTrack = cms.string("tracker"),
            useState = cms.string("atVertex"),
            useSimpleGeometry = cms.bool(True),
            useStation2 = cms.bool(False),
            fallbackToME1 = cms.bool(False),
            cosmicPropagationHypothesis = cms.bool(False),
            useMB2InOverlap = cms.bool(False),
            propagatorAlong = cms.ESInputTag("", "SteppingHelixPropagatorAlong"),
            propagatorAny = cms.ESInputTag("", "SteppingHelixPropagatorAny"),
            propagatorOpposite = cms.ESInputTag("", "SteppingHelixPropagatorOpposite")
        ),
        # Muon track extrapolation to 2nd station
        muProp2nd = cms.PSet(
            useTrack = cms.string("none"),
            useState = cms.string("atVertex"),
            useSimpleGeometry = cms.bool(False),
            useStation2 = cms.bool(True),
            fallbackToME1 = cms.bool(False),
            cosmicPropagationHypothesis = cms.bool(False),
            useMB2InOverlap = cms.bool(True),
            propagatorAlong = cms.ESInputTag("", "SteppingHelixPropagatorAlong"),
            propagatorAny = cms.ESInputTag("", "SteppingHelixPropagatorAny"),
            propagatorOpposite = cms.ESInputTag("", "SteppingHelixPropagatorOpposite")
        )
    )

    ## Producer de propagación analítica a MB2/ME2
    ## Usa extrapolación geométrica sin campo magnético
    '''process.genParticlePropagatorAnalytic = cms.EDProducer("GenParticlePropagatorAnalytic",
        src = cms.InputTag("finalGenParticles"),
        # Barrel (MB2) parameters
        mb2_r = cms.double(512.401),           # MB2 barrel radius (cm)
        mb2_z_max = cms.double(900.0),         # MB2 barrel z extent (cm)
        # Endcap (ME2) parameters
        me2_z = cms.double(830.0),             # ME2 endcap z position (cm)
        me2_r_min = cms.double(20.0),          # ME2 endcap inner radius (cm)
        me2_r_max = cms.double(800.0),         # ME2 endcap outer radius (cm)
        # Region boundaries
        barrelMaxEta = cms.double(1.2)         # |eta| < 1.2 => barrel, else endcap
    )
'''
    ## Añadir coordenadas propagadas a la tabla
    genParticleTable.externalVariables = cms.PSet(
        etaSt2 = ExtVar(cms.InputTag("genParticlePropagator", "etaSt2"), "float", doc="pseudorapidity at MB2 (barrel) or ME2 (endcap)", precision=8),
        phiSt2 = ExtVar(cms.InputTag("genParticlePropagator", "phiSt2"), "float", doc="azimuth at MB2 (barrel) or ME2 (endcap)", precision=8),
        etaSt1 = ExtVar(cms.InputTag("genParticlePropagator", "etaSt1"), "float", doc="pseudorapidity at MB1 (barrel) or ME1 (endcap)", precision=8),
        phiSt1 = ExtVar(cms.InputTag("genParticlePropagator", "phiSt1"), "float", doc="azimuth at MB1 (barrel) or ME1 (endcap)", precision=8),

    )

    ## Añadir el producer al task
    process.l1tPh2NanoTask.add(process.genParticlePropagator)
    
    ## add pruned gen particles a la Mini
    if False: 
        ## Gen all 
        # genParticleTable.src = "genParticles" # see 
        ## Mini default, see  https://github.com/cms-sw/cmssw/blob/master/PhysicsTools/PatAlgos/python/slimming/prunedGenParticles_cfi.py
        # genParticleTable.src = "prunedGenParticles"
        ## Nano default, see https://github.com/cms-sw/cmssw/blob/master/PhysicsTools/NanoAOD/python/genparticles_cff.py#L8
        # genParticleTable.src = "finalGenParticles" 

        process.prunedGenParticleTable = genParticleTable.clone()
        process.prunedGenParticleTable.src = "prunedGenParticles"
        process.prunedGenParticleTable.name = "prunedGenPart"
        process.l1tPh2NanoTask.add(process.prunedGenParticleTable)

    # lower genVisTau pt threshold
    #process.genVisTauTable.cut = "pt > 1"
    # lower AK8 gen jet threshold
    #process.genJetAK8Table.cut = "pt > 10"

    process.l1tPh2NanoTask.add(
                puTable, metMCTable,
                genParticleTask, genParticleTablesTask,
    )
    
    # add all GenJets: AK4 and AK8
    process.l1tPh2NanoTask.add(genJetTable,patJetPartonsNano,genJetFlavourTable)
    process.l1tPh2NanoTask.add(genJetAK8Table,genJetAK8FlavourAssociation,genJetAK8FlavourTable)

    return process

# GMT stub ↔ gen muon matching at second station (uses propagated MB2 coordinates)
def addGMTStubGenMatching(process,
                          stubSrc="simMuonGmtStubs",
                          genSrc="finalGenParticles",
                          propagatorLabel="genParticlePropagatorAnalytic",
                          deltaRMax=0.3):
    # Necesita que genParticlePropagatorAnalytic esté en el task para tener eta/phi/r en MB2/ME2
    process.gmtStubGenMatcher = cms.EDProducer(
        "GMTStubGenMatcher",
        stubSrc=cms.InputTag(stubSrc),
        genSrc=cms.InputTag(genSrc),
        etaSt2=cms.InputTag(propagatorLabel, "etaSt2"),
        phiSt2=cms.InputTag(propagatorLabel, "phiSt2"),
        deltaRMax=cms.double(deltaRMax),
    )

    
    process.l1tPh2NanoTask.add(process.gmtStubGenMatcher)
    return process


def addFullPh2L1Nano(process):
    addGenObjects(process)
    addPh2L1Objects(process)
    addPh2GTObjects(process)

    return process


def addPh2L1MuonObjects(process):
    addGenObjects(process)
    process.l1tPh2NanoTask.add(p2L1MuTablesTask)
    return process
