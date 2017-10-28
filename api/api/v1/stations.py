from flask_restful import Resource, reqparse

class StationsCtrl(Resource):
    # ${HOSTNAME}/v1/api/stations
    # will return an array of stations (JSON objects)
    def get(self):
        return [
        { "uid" : "1", "name" : "Aeschenplatz", "longitude" : "47.551430", "latitude" : "7.595150", "traveltime" : 0},
        { "uid" : "2", "name" : "Basel SBB", "longitude" : "47.548418", "latitude" : "7.590301", "traveltime" : 5}
    ]
