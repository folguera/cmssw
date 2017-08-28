/**
  \class    TSGForOI
  \brief    Create L3MuonTrajectorySeeds from L2 Muons updated at vertex in an outside in manner
  \author   Benjamin Radburn-Smith, Santiago Folgueras
*/

#include "RecoMuon/TrackerSeedGenerator/plugins/TSGForOI.h"
#include "DataFormats/TrackerCommon/interface/TrackerTopology.h"

#include <memory>

using namespace edm;
using namespace std;

TSGForOI::TSGForOI(const edm::ParameterSet & iConfig) :
  src_(consumes<reco::TrackCollection>(iConfig.getParameter<edm::InputTag>("src"))),
  numOfMaxSeedsParam_(iConfig.getParameter<uint32_t>("maxSeeds")),
  numOfLayersToTry_(iConfig.getParameter<int32_t>("layersToTry")),
  numOfHitsToTry_(iConfig.getParameter<int32_t>("hitsToTry")),
  fixedErrorRescalingForHits_(iConfig.getParameter<double>("fixedErrorRescaleFactorForHits")),
  fixedErrorRescalingForHitless_(iConfig.getParameter<double>("fixedErrorRescaleFactorForHitless")),
  adjustErrorsDynamicallyForHits_(iConfig.getParameter<bool>("adjustErrorsDynamicallyForHits")),
  adjustErrorsDynamicallyForHitless_(iConfig.getParameter<bool>("adjustErrorsDynamicallyForHitless")),
  estimatorName_(iConfig.getParameter<std::string>("estimator")),
  minEtaForTEC_(iConfig.getParameter<double>("minEtaForTEC")),
  maxEtaForTOB_(iConfig.getParameter<double>("maxEtaForTOB")),
  useHitLessSeeds_(iConfig.getParameter<bool>("UseHitLessSeeds")),
  useStereoLayersInTEC_(iConfig.getParameter<bool>("UseStereoLayersInTEC")),
  updator_(new KFUpdator()),
  measurementTrackerTag_(consumes<MeasurementTrackerEvent>(iConfig.getParameter<edm::InputTag>("MeasurementTrackerEvent"))),
  pT1_(iConfig.getParameter<double>("pT1")),
  pT2_(iConfig.getParameter<double>("pT2")),
  pT3_(iConfig.getParameter<double>("pT3")),
  eta1_(iConfig.getParameter<double>("eta1")),
  eta2_(iConfig.getParameter<double>("eta2")),
  SF1_(iConfig.getParameter<double>("SF1")),
  SF2_(iConfig.getParameter<double>("SF2")),
  SF3_(iConfig.getParameter<double>("SF3")),
  SF4_(iConfig.getParameter<double>("SF4")),
  SF5_(iConfig.getParameter<double>("SF5")),
  tsosDiff_(iConfig.getParameter<double>("tsosDiff")),
  propagatorName_(iConfig.getParameter<std::string>("propagatorName")),
  theCategory(string("Muon|RecoMuon|TSGForOI"))
{
  produces<std::vector<TrajectorySeed> >();
}


TSGForOI::~TSGForOI(){
}


void TSGForOI::produce(edm::StreamID sid, edm::Event& iEvent, const edm::EventSetup& iSetup) const {
  /// Init variables
  unsigned int numOfMaxSeeds = numOfMaxSeedsParam_;
  unsigned int numSeedsMade=0;
  bool analysedL2 = false;
  bool foundHitlessSeed = false; 
  unsigned int layerCount = 0;


  /// Surface used to make a TSOS at the PCA to the beamline
  Plane::PlanePointer dummyPlane = Plane::build(Plane::PositionType(), Plane::RotationType());

  /// Read ESHandles
  edm::Handle<MeasurementTrackerEvent>          measurementTrackerH;
  edm::ESHandle<Chi2MeasurementEstimatorBase>   estimatorH;
  edm::ESHandle<MagneticField>                  magfieldH;
  edm::ESHandle<Propagator>                     propagatorAlongH;
  edm::ESHandle<Propagator>                     propagatorOppositeH;
  edm::ESHandle<GlobalTrackingGeometry>         geometryH;

  iSetup.get<IdealMagneticFieldRecord>().get(magfieldH);
  iSetup.get<TrackingComponentsRecord>().get(propagatorName_, propagatorOppositeH);
  iSetup.get<TrackingComponentsRecord>().get(propagatorName_, propagatorAlongH);
  iSetup.get<GlobalTrackingGeometryRecord>().get(geometryH);
  iSetup.get<TrackingComponentsRecord>().get(estimatorName_,estimatorH);
  iEvent.getByToken(measurementTrackerTag_, measurementTrackerH);

  /// Read L2 track collection
  edm::Handle<reco::TrackCollection> l2TrackCol;
  iEvent.getByToken(src_, l2TrackCol);

  //	The product:
  std::unique_ptr<std::vector<TrajectorySeed> > result(new std::vector<TrajectorySeed>());

  //	Get vector of Detector layers once:
  std::vector<BarrelDetLayer const*> const& tob          = measurementTrackerH->geometricSearchTracker()->tobLayers();
  std::vector<ForwardDetLayer const*> const& tecPositive = measurementTrackerH->geometricSearchTracker()->posTecLayers();
  std::vector<ForwardDetLayer const*> const& tecNegative = measurementTrackerH->geometricSearchTracker()->negTecLayers();
  edm::ESHandle<TrackerTopology> tTopo_handle;
  iSetup.get<TrackerTopologyRcd>().get(tTopo_handle);
  const TrackerTopology* tTopo = tTopo_handle.product();

  //	Get the suitable propagators:
  edm::ESHandle<Propagator> SmartOpposite;
  edm::ESHandle<Propagator> SHPOpposite;
  iSetup.get<TrackingComponentsRecord>().get("hltESPSmartPropagatorAnyOpposite", SmartOpposite);
  iSetup.get<TrackingComponentsRecord>().get("hltESPSteppingHelixPropagatorOpposite", SHPOpposite);

  std::unique_ptr<Propagator> propagatorAlong = SetPropagationDirection(*propagatorAlongH,alongMomentum);
  std::unique_ptr<Propagator> propagatorOpposite= SetPropagationDirection(*propagatorOppositeH,oppositeToMomentum);
  //  std::unique_ptr<Propagator> propagatorOpposite= SetPropagationDirection(*SmartOpposite,alongMomentum);
  
  
  //	Loop over the L2's and make seeds for all of them:
  LogTrace(theCategory) << "TSGForOI::produce: Number of L2's: " << l2TrackCol->size();
  for (unsigned int l2TrackColIndex(0);l2TrackColIndex!=l2TrackCol->size();++l2TrackColIndex){
    const reco::TrackRef l2(l2TrackCol, l2TrackColIndex);
    std::unique_ptr<std::vector<TrajectorySeed> > out(new std::vector<TrajectorySeed>());
    LogTrace("TSGForOI") << "TSGForOI::produce: L2 muon pT, eta, phi --> " << l2->pt() << " , " << l2->eta() << " , " << l2->phi() << endl;
    
    FreeTrajectoryState fts = trajectoryStateTransform::initialFreeState(*l2, magfieldH.product());
    dummyPlane->move(fts.position() - dummyPlane->position());
    TrajectoryStateOnSurface tsosAtIP = TrajectoryStateOnSurface(fts, *dummyPlane);
    LogTrace("TSGForOI") << "TSGForOI::produce: Created TSOSatIP: " << tsosAtIP << std::endl;
    
    numSeedsMade=0;
    analysedL2 = false;
    
    if (useHitLessSeeds_){  //  
      StateOnTrackerBound onBounds(propagatorAlong.get());
      TrajectoryStateOnSurface outer = onBounds(fts);
      if (outer.isValid()){
	double errorSFHitless=1.0;
	if (!adjustErrorsDynamicallyForHitless_) errorSFHitless = fixedErrorRescalingForHitless_;
	else                                     errorSFHitless = calculateSFFromL2(l2);
	outer.rescaleError(errorSFHitless);
	
	if (findHitlessSeeds(outer, *(propagatorOpposite.get()), l2, estimatorH, measurementTrackerH, out)) {
	  numSeedsMade++;
	  foundHitlessSeed = true;
	}
      }
    }
    //   
    //		BARREL
    if (std::abs(l2->eta()) < maxEtaForTOB_) {
      layerCount = 0;
      for (auto it=tob.rbegin(); it!=tob.rend(); ++it) {	//This goes from outermost to innermost layer
	LogTrace("TSGForOI") << "TSGForOI::produce: looping in TOB layer " << layerCount << endl; 
	findSeedsOnLayer(tTopo, **it, tsosAtIP,  *(propagatorAlong.get()), *(propagatorOpposite.get()), l2, 
			 estimatorH, measurementTrackerH, numSeedsMade, numOfMaxSeeds, layerCount, foundHitlessSeed, analysedL2, out);
      }
    }
    
    //		Reset Number of seeds if in overlap region:
    if (std::abs(l2->eta()) > minEtaForTEC_ && std::abs(l2->eta()) < maxEtaForTOB_){
      numSeedsMade=0;
    }
    
    //		ENDCAP+
    if (l2->eta() > minEtaForTEC_) {
      layerCount = 0;
      for (auto it=tecPositive.rbegin(); it!=tecPositive.rend(); ++it) {
	LogTrace("TSGForOI") << "TSGForOI::produce: looping in TEC+ layer " << layerCount << endl; 
	findSeedsOnLayer(tTopo, **it, tsosAtIP,  *(propagatorAlong.get()), *(propagatorOpposite.get()), l2, 
			 estimatorH, measurementTrackerH, numSeedsMade, numOfMaxSeeds, layerCount, foundHitlessSeed, analysedL2, out);
      }
    }

    //		ENDCAP-
    if (l2->eta() < -minEtaForTEC_) {
      layerCount = 0;
      for (auto it=tecNegative.rbegin(); it!=tecNegative.rend(); ++it) {
	LogTrace("TSGForOI") << "TSGForOI::produce: looping in TEC- layer " << layerCount << endl; 
	findSeedsOnLayer(tTopo, **it, tsosAtIP,  *(propagatorAlong.get()), *(propagatorOpposite.get()), l2, 
			 estimatorH, measurementTrackerH, numSeedsMade, numOfMaxSeeds, layerCount, foundHitlessSeed, analysedL2, out);
      }
    }

    for (std::vector<TrajectorySeed>::iterator it=out->begin(); it!=out->end(); ++it){
      result->push_back(*it);
    }
  } //L2Collection
  edm::LogInfo(theCategory) << "TSGForOI::produce: number of seeds made: " << result->size();
  
  iEvent.put(std::move(result));
}
bool TSGForOI::findHitlessSeeds(const TrajectoryStateOnSurface &outer,
				const Propagator& propagatorOpposite,	
				const reco::TrackRef l2,
				edm::ESHandle<Chi2MeasurementEstimatorBase>& estimatorH,
				edm::Handle<MeasurementTrackerEvent>& measurementTrackerH,
				std::unique_ptr<std::vector<TrajectorySeed> >& out
				) const{
  
  bool found = false;
  if (!outer.isValid()) return false;
  
  std::vector<BarrelDetLayer const*> const& tob          = measurementTrackerH->geometricSearchTracker()->tobLayers();
  std::vector<ForwardDetLayer const*> const& tecPositive = measurementTrackerH->geometricSearchTracker()->posTecLayers();
  std::vector<ForwardDetLayer const*> const& tecNegative = measurementTrackerH->geometricSearchTracker()->negTecLayers();
  
  double z = outer.globalPosition().z();	
  unsigned int layerShift=0;
  const DetLayer *inLayer = 0;
  if (fabs(z) < tecPositive.front()->surface().position().z()  ){
    inLayer = *(tob.rbegin()+layerShift);
    LogTrace(theCategory)<<"choosing TOB layer with shift: "<<layerShift;
  } 
  else {
    unsigned int tecIt=1;
    for (; tecIt!=tecPositive.size();tecIt++){
      LogTrace("TSGForOI")<<"checking surface with shift: "<<tecIt
			  <<"z: "<<tecPositive[tecIt]->surface().position().z();
      if (fabs(z) < tecPositive[tecIt]->surface().position().z()){
	inLayer = ( z < 0 ) ? tecNegative[tecIt-1] : tecPositive[tecIt-1] ; 
	layerShift=tecIt-1;
	LogTrace("TSGForOI")<<"choosing TEC layer with shift: "<<layerShift
			    <<" and z: "<<inLayer->surface().position().z();
	break;
      }
    }
    if (!inLayer) {
      inLayer = ( z < 0 ) ? tecNegative.back() : tecPositive.back();
      LogTrace(theCategory)<<"choosing last TEC layer with z: "<<inLayer->surface().position().z();
    }
  }
  
  //find out at least one compatible detector reached
  std::vector< DetLayer::DetWithState > compatible;
  compatible.reserve(10);
  inLayer->compatibleDetsV(outer,propagatorOpposite,*estimatorH,compatible);
  
  //loop the parts until at least a compatible is found
  while (compatible.size()==0) {
    switch ( GeomDetEnumerators::subDetGeom[inLayer->subDetector()] ) {
    case GeomDetEnumerators::PixelBarrel:
    case GeomDetEnumerators::PixelEndcap:
    case GeomDetEnumerators::TIB:
    case GeomDetEnumerators::TID:
    case GeomDetEnumerators::TOB:
      layerShift++;
      if (layerShift>=tob.size()){
	LogDebug(theCategory) <<"all barrel layers are exhausted to find starting state. no seed,";
	return false;
      }
      inLayer = *(tob.rbegin()+layerShift);
      break;
    case GeomDetEnumerators::TEC:
      if (layerShift==0){
	LogDebug(theCategory) <<"failed to get a compatible module on a TEC layer, using the last TOB layer.";
	inLayer = *(tob.rbegin()+layerShift);
      }
      else{
	layerShift--;
	LogDebug(theCategory) <<"reaching more in with layer "<<layerShift<<" in TEC";
	inLayer = ( z < 0 ) ? tecNegative[layerShift] : tecPositive[layerShift] ;
      }
      break;
    default:
      edm::LogError(theCategory)<<"subdetectorid is not a tracker sub-dectector id. skipping.";
      return false;
    }
    inLayer->compatibleDetsV(outer,propagatorOpposite,*estimatorH,compatible);
  }
  if (!compatible.empty()){
    // STORE ONE HITLESS PER L2: 
    auto const& detOnLayer  = compatible.front().first;
    auto const& tsosOnLayer = compatible.front().second;
    //      dets.front().second.rescaleError(errorSFHitless);
    PTrajectoryStateOnDet const& ptsod = trajectoryStateTransform::persistentState(tsosOnLayer,detOnLayer->geographicalId().rawId());
    TrajectorySeed::recHitContainer rHC;
    out->push_back(TrajectorySeed(ptsod,rHC,oppositeToMomentum));
    found = true; // do we need this? 
  }
  return found;
}

void TSGForOI::findSeedsOnLayer(
				const TrackerTopology* tTopo,
				const GeometricSearchDet &layer,
				const TrajectoryStateOnSurface &tsosAtIP,
				const Propagator& propagatorAlong,
				const Propagator& propagatorOpposite,
				const reco::TrackRef l2,
				edm::ESHandle<Chi2MeasurementEstimatorBase>& estimatorH,
				edm::Handle<MeasurementTrackerEvent>& measurementTrackerH,
				unsigned int& numSeedsMade,
				unsigned int& numOfMaxSeeds,
				unsigned int& layerCount,
				bool& foundHitlessSeed,
				bool& analysedL2,
				std::unique_ptr<std::vector<TrajectorySeed> >& out)  const{
  
  if (numSeedsMade>numOfMaxSeeds) return;
  LogTrace("TSGForOI") << "TSGForOI::findSeedsOnLayer: numSeedsMade = " << numSeedsMade << " , layerCount = " <<  layerCount << endl;
  
  double errorSFHits=1.0;
  double errorSFHitless=1.0;
  if (!adjustErrorsDynamicallyForHits_) errorSFHits = fixedErrorRescalingForHits_;
  else                                  errorSFHits = calculateSFFromL2(l2);
  if (!adjustErrorsDynamicallyForHitless_) errorSFHitless = fixedErrorRescalingForHitless_;

  // Hitless:  TO-BE  DISCARDED.
  if (useHitLessSeeds_ && !foundHitlessSeed) {
    LogTrace("TSGForOI") << "TSGForOI::findSeedsOnLayer: Start hitless" << endl;
    std::vector< GeometricSearchDet::DetWithState > dets;
    layer.compatibleDetsV(tsosAtIP, propagatorAlong, *estimatorH, dets);
    if (dets.size()>0) {  
      auto const& detOnLayer = dets.front().first;
      auto const& tsosOnLayer = dets.front().second;
      LogTrace("TSGForOI") << "TSGForOI::findSeedsOnLayer: tsosOnLayer " << tsosOnLayer << endl;
      if (!tsosOnLayer.isValid()){
	edm::LogInfo(theCategory) << "ERROR!: Hitless TSOS is not valid!";
      }
      else{
	// calculate SF from L2 (only once -- if needed)
	if (!analysedL2 && adjustErrorsDynamicallyForHitless_) {
	  errorSFHitless=calculateSFFromL2(l2);
	  analysedL2=true;
	}
	
	dets.front().second.rescaleError(errorSFHitless);
	PTrajectoryStateOnDet const& ptsod = trajectoryStateTransform::persistentState(tsosOnLayer,detOnLayer->geographicalId().rawId());
	TrajectorySeed::recHitContainer rHC;
	out->push_back(TrajectorySeed(ptsod,rHC,oppositeToMomentum));
	LogTrace("TSGForOI") << "TSGForOI::findSeedsOnLayer: TSOD (Hitless) done " << endl;
	foundHitlessSeed=true;
	numSeedsMade++;
      }
    }
  }
  //  numSeedsMade=out->size();
  

  // Hits:
  if (layerCount>numOfLayersToTry_) return;
  LogTrace("TSGForOI") << "TSGForOI::findSeedsOnLayer: Start Hits" <<endl;  
  if (makeSeedsFromHits(tTopo, layer, tsosAtIP, *out, propagatorAlong, propagatorOpposite, *measurementTrackerH, estimatorH, numSeedsMade, errorSFHits))  ++layerCount; 
}

double TSGForOI::calculateSFFromL2(const reco::TrackRef track) const{

  double theSF=1.0;
  //	L2 direction vs pT blowup - as was previously done:
  //	Split into 4 pT ranges: <pT1_, pT1_<pT2_, pT2_<pT3_, <pT4_: 13,30,70
  //	Split into 2 eta ranges for the middle two pT ranges: 1.0,1.4
  double abseta = std::abs(track->eta());
  if (track->pt()<=pT1_) theSF=SF1_;
  if (track->pt()>pT1_ && track->pt()<=pT2_){
    if (abseta<=eta1_) theSF=SF3_;
    if (abseta>eta1_ && abseta<=eta2_) theSF=SF2_;
    if (abseta>eta2_) theSF=SF3_;
  }
  if (track->pt()>pT2_ && track->pt()<=pT3_){
    if (abseta<=eta1_) theSF=SF5_;
    if (abseta>eta1_ && abseta<=eta2_) theSF=SF4_;
    if (abseta>eta2_) theSF=SF5_;
  }
  if (track->pt()>pT3_) theSF=SF5_;

  LogTrace(theCategory) << "TSGForOI::calculateSFFromL2: SF has been calculated as: " << theSF;
  return theSF;
}


int TSGForOI::makeSeedsFromHits(
				const TrackerTopology* tTopo,
				const GeometricSearchDet &layer,
				const TrajectoryStateOnSurface &tsosAtIP,
				std::vector<TrajectorySeed> &out,
				const Propagator& propagatorAlong,
				const Propagator& propagatorOpposite,
				const MeasurementTrackerEvent &measurementTracker,
				edm::ESHandle<Chi2MeasurementEstimatorBase>& estimatorH,
				unsigned int& numSeedsMade,
				const double errorSF)  const{

  //		Error Rescaling:
  TrajectoryStateOnSurface onLayer(tsosAtIP);
  onLayer.rescaleError(errorSF);    
  
  std::vector< GeometricSearchDet::DetWithState > dets;
  layer.compatibleDetsV(onLayer, propagatorOpposite, *estimatorH, dets);
  
  //	Find Measurements on each DetWithState:
  LogTrace("TSGForOI") << "TSGForOI::findSeedsOnLayer: find measurements on each detWithState  " << dets.size() << endl;
  std::vector<TrajectoryMeasurement> meas;
  for (std::vector<GeometricSearchDet::DetWithState>::iterator it=dets.begin(); it!=dets.end(); ++it) {
    MeasurementDetWithData det = measurementTracker.idToDet(it->first->geographicalId());
    if (det.isNull()) {
      continue;
    }
    if (!it->second.isValid()) continue;	//Skip if TSOS is not valid

    std::vector < TrajectoryMeasurement > mymeas = det.fastMeasurements(it->second, onLayer, propagatorAlong, *estimatorH);	//Second TSOS is not used
    for (std::vector<TrajectoryMeasurement>::const_iterator it2 = mymeas.begin(), ed2 = mymeas.end(); it2 != ed2; ++it2) {
      if (it2->recHit()->isValid()) meas.push_back(*it2);	//Only save those which are valid
    }
  }
  
  
  //	Update TSOS using TMs after sorting, then create Trajectory Seed and put into vector:
  LogTrace("TSGForOI") << "TSGForOI::findSeedsOnLayer: Update TSOS using TMs after sorting, then create Trajectory Seed, number of TM = " << meas.size() << endl;
  unsigned int found = 0;
  std::sort(meas.begin(), meas.end(), TrajMeasLessEstim());
  for (std::vector<TrajectoryMeasurement>::const_iterator it=meas.begin(); it!=meas.end(); ++it) {
    TrajectoryStateOnSurface updatedTSOS = updator_->update(it->forwardPredictedState(), *it->recHit());
    LogTrace("TSGForOI") << "TSGForOI::findSeedsOnLayer: TSOS for TM " << found << endl;
    if (not updatedTSOS.isValid()) continue;

    // CHECK if is StereoLayer: 
    if (useStereoLayersInTEC_) { 
      DetId detid = ((*it).recHit()->hit())->geographicalId();
      if (detid.subdetId() == StripSubdetector::TEC) {
	if (!tTopo->tecIsStereo(detid.rawId())) break;  // try another layer
      }
    }
    
    edm::OwnVector<TrackingRecHit> seedHits;
    seedHits.push_back(*it->recHit()->hit());
    PTrajectoryStateOnDet const& pstate = trajectoryStateTransform::persistentState(updatedTSOS, it->recHit()->geographicalId().rawId());
    TrajectorySeed seed(pstate, std::move(seedHits), alongMomentum);
    LogTrace("TSGForOI") << "TSGForOI::findSeedsOnLayer: number of seedHits: " << seedHits.size() << endl;
    out.push_back(seed);
    found++;
    numSeedsMade++;
    if (found == numOfHitsToTry_) break;
  }
  return found;
}


void TSGForOI::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  edm::ParameterSetDescription desc;
  desc.add<edm::InputTag>("src",edm::InputTag("hltL2Muons","UpdatedAtVtx"));
  desc.add<int>("layersToTry",1);
  desc.add<double>("fixedErrorRescaleFactorForHitless",2.0);
  desc.add<int>("hitsToTry",1);
  desc.add<bool>("adjustErrorsDynamicallyForHits",false);
  desc.add<bool>("adjustErrorsDynamicallyForHitless",false);
  desc.add<edm::InputTag>("MeasurementTrackerEvent",edm::InputTag("hltSiStripClusters"));
  desc.add<bool>("UseHitLessSeeds",true);
  desc.add<bool>("UseStereoLayersInTEC",false);
  desc.add<std::string>("estimator","hltESPChi2MeasurementEstimator100");
  desc.add<double>("maxEtaForTOB",1.2);
  desc.add<double>("minEtaForTEC",0.8);
  desc.addUntracked<bool>("debug",true);
  desc.add<double>("fixedErrorRescaleFactorForHits",2.0);
  desc.add<unsigned int>("maxSeeds",1);
  desc.add<double>("pT1",13.0);
  desc.add<double>("pT2",30.0);
  desc.add<double>("pT3",70.0);
  desc.add<double>("eta1",1.0);
  desc.add<double>("eta2",1.4);
  desc.add<double>("SF1",3.0);
  desc.add<double>("SF2",4.0);
  desc.add<double>("SF3",5.0);
  desc.add<double>("SF4",7.0);
  desc.add<double>("SF5",10.0);
  desc.add<double>("tsosDiff",0.03);
  desc.add<std::string>("propagatorName","PropagatorWithMaterial");
  descriptions.add("TSGForOI",desc);
}

DEFINE_FWK_MODULE(TSGForOI);
