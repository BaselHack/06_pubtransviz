from flask_restful import Resource, reqparse
from pymongo import MongoClient
import json

from bson.json_util import dumps


class ConnectionsCtrl(Resource):
    # ${HOSTNAME}/v1/api/connections
    # will return an array of stations (JSON objects)
    def get(self):
        # parser = reqparse.RequestParser()
        # parser.add_argument('longitude', type=str)
        # parser.add_argument('latitude', type=str)
        #
        # arguments = parser.parse_args()
        #
        # longitude = arguments['longitude']
        # latitude = arguments['latitude']
        #
        # if(longitude is not None and latitude is not None):
        #     computeHeatMap(longitude, latitude)

        dbname = 'PubTransViz'
        dbcoll = 'connections'
        client = MongoClient()
        state = client[dbname][dbcoll]
        connections = json.loads(dumps(state.find({})))
        client.close()
        return connections
