from flask_restful import Resource, reqparse
from pymongo import MongoClient
import json

from bson.json_util import dumps


class StationsCtrl(Resource):
    # ${HOSTNAME}/v1/api/stations
    # will return an array of stations (JSON objects)
    def get(self):
        dbname = 'PubTransViz'
        dbcoll = 'stations'
        client = MongoClient()
        state = client[dbname][dbcoll]
        stations = json.loads(dumps(state.find({})))
        client.close()
        return stations
