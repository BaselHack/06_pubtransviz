from flask_restful import Resource, reqparse
from pymongo import MongoClient
import json

from bson.json_util import dumps


class StationsCtrl(Resource):
    # ${HOSTNAME}/v1/api/stations
    # will return an array of stations (JSON objects)
    def get(self):
        
        parser = reqparse.RequestParser()
        parser.add_argument('longitude', type=str)
        parser.add_argument('latitude', type=str)

        arguments = parser.parse_args()
        
        longitude = arguments['longitude']
        latitude = arguments['latitude']
        
        if(longitude is not None and latitude is not None):
            computeHeatMap(longitude, latitude)
        
        dbname = 'PubTransViz'
        dbcoll = 'stations'
        client = MongoClient()
        state = client[dbname][dbcoll]
        stations = json.loads(dumps(state.find({})))
        client.close()
        return stations


def buildConnectionMatrix():
    dbname = 'PubTransViz'
    dbcoll = 'stations'
    client = MongoClient()
    state = client[dbname][dbcoll]
    stations = json.loads(dumps(state.find({})))
    count = stations.count
    
    db = client['PubTransViz']
    connections = db.connections
    
    connectionMatrix = []
    for x in range(0, count):
        connectionMatrix[0] = []
        
        stationX = stations.find({'_id' : x})
        
        for y in range(0, count):
    
            stationY = stations.find({'_id' : y})
            connection = connections.find({'start_station_uid' : stationX['uid'], 'end_station_uid' : stationY['uid']})
            connectionMatrix[x][y] = connection #most will be None
    
    

connectionMatrix = buildConnectionMatrix()

def computeHeatMap(longitude, latitude):
    chosen_station = stations.find({'longitude': {'$near': longitude}, 'longitude': {'$near': latitude}})
    
    # maybe this can be done better, but we are in a hurry, I just need the count
    stations = json.loads(dumps(state.find({})))
    count = stations.count
    
    stationsAsResult = []
    for(i in range(0, count)):
        stationsAsResult[i] = None
    
    startStationId = int(chosen_station['_id'])
    
    stationsAsResult[startStationId] = stations.find({'_id' :  startStationId})
    stationsAsResult[startStationId]['travelTime'] = 0 # travel time is zero at starting point
    
    traveltime = 0
    stationsAsResult = computeTravelTimeFromStation(startStationId, stationsAsResult, traveltime)
    return stationsAsResult


            
def computeTravelTimeFromStation(stationId, stationsAsResult, traveltime):
    
    #break condition, don't continue to iterate if all stations are calcualted
    
    allStationsCalcualted = true
    for (station in stationsAsResult):
        if(station is None):
            allStationsCalcualted = false
    
    if(allStationsCalcualted)
        return stationsAsResult
    
    #actual calculation
    
    connectionRow = connectionMatrix[stationId]
    for (connection in connectionRow):
        if(connection is not None):
            # check if we already have the station in the list, if not add it with the travel-times
            arrivalStationid = int(connection['end_station_id'])
            arrivalStation = stationsAsResult[arrivalStationid]
            
            if(arrivalStation is None):
                stationsAsResult[arrivalStationid] = stations.find({'_id' : arrivalStationid})
                arrivalStation = stationsAsResult[arrivalStationid]
            currentTravelTime = traveltime + float(connection['travel_time'])
            arrivalStation['travelTime'] = currentTravelTime
            
            stationsAsResult = computeTravelTimeFromStation(int(arrivalStation['_id']), stationsAsResult, currentTravelTime)
            
    return stationsAsResult
                
            
            
    
    
    
    
