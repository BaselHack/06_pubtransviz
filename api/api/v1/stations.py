from flask_restful import Resource, reqparse
from pymongo import MongoClient
import json

from bson.json_util import dumps

from datetime import datetime, timedelta


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
    print("building in-memory connection matrix")
    dbname = 'PubTransViz'
    dbcoll = 'stations'
    client = MongoClient()
    state = client[dbname][dbcoll]
    stations = json.loads(dumps(state.find({})))

    count = len(stations)

    db = client['PubTransViz']
    connections = db.connections
    stations = db.stations

    connectionMatrix = []
    for x in range(0, count):
        connectionMatrix.append([])

        stationX = stations.find_one({'_id' : x})

        for y in range(0, count):

            stationY = stations.find_one({'_id' : y})
            connection = connections.find_one({'start_station_uid' : stationX['uid'], 'end_station_uid' : stationY['uid']})
            connectionMatrix[x].append(connection) #most will be None
    print("building in-memory connection matrix done!")
    return connectionMatrix

#connectionMatrix = buildConnectionMatrix()
connectionMatrix = None


def computeHeatMap(longitude, latitude):
    dbname = 'PubTransViz'
    dbcoll = 'stations'
    client = MongoClient()
    state = client[dbname][dbcoll]
    db = client['PubTransViz']
    connections = db.connections
    stations = db.stations

    chosen_station = stations.find_one({'coordinates': {'$near': [longitude, latitude]}})
    print('selected station ' + chosen_station['uid'])

    # maybe this can be done better, but we are in a hurry, I just need the count
    jsonStations = json.loads(dumps(state.find({})))
    count = len(jsonStations)

    stationsAsResult = []
    for i in range(0, count):
        stationsAsResult.append(None)

    startStationId = int(chosen_station['_id'])
    print('station id ' + str(startStationId))
    stationsAsResult[startStationId] = stations.find_one({'_id' :  startStationId})

    traveltime = parseToTimeDelta("0:00:00")
    stationsAsResult[startStationId]['travelTime'] = str(traveltime) # travel time is zero at starting point

    stationsAsResult = computeTravelTimeFromStation(startStationId, stationsAsResult, traveltime)
    return stationsAsResult

def parseToTimeDelta(string_date):
    t = datetime.strptime(string_date,"%H:%M:%S")
    #use datetime's hour, min and sec properties to build a timedelta
    delta = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
    return delta

def computeTravelTimeFromStation(stationId, stationsAsResult, traveltime):
    global connectionMatrix
    #break condition, don't continue to iterate if all stations are calcualted

    allStationsCalcualted = True
    for station in stationsAsResult:
        if(station is None):
            allStationsCalcualted = False

    if(allStationsCalcualted):
        return stationsAsResult

    client = MongoClient()
    db = client['PubTransViz']
    connections = db.connections
    stations = db.stations

    #actual calculation

    if(connectionMatrix is None):
        connectionMatrix = buildConnectionMatrix()

    connectionRow = connectionMatrix[stationId]
    for connection in connectionRow:
        if(connection is not None):
            # check if we already have the station in the list, if not add it with the travel-times
            arrivalStationid = int(connection['end_station_id'])
            arrivalStation = stationsAsResult[arrivalStationid]

            if(arrivalStation is None):
                stationsAsResult[arrivalStationid] = stations.find_one({'_id' : arrivalStationid})
                arrivalStation = stationsAsResult[arrivalStationid]
            currentTravelTime = traveltime + parseToTimeDelta(connection['travel_time'])
            arrivalStation['travelTime'] = str(currentTravelTime)

            stationsAsResult = computeTravelTimeFromStation(int(arrivalStation['_id']), stationsAsResult, currentTravelTime)

    return stationsAsResult


# entry point for testing
if __name__ == '__main__':
    print(json.dumps(computeHeatMap(47.551365, 7.594903)))
