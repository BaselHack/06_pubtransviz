from flask import Flask
from flask_restful import Api
from api.v1 import stations

from flask_cors import CORS

app = Flask(__name__)
# Enabling CORS
CORS(app, resources={r"/api/v1/*": {"origins": "*"}})
# API Instantiation
api = Api(app)
# Stations Endpoint
api.add_resource(stations.StationsCtrl, '/api/v1/stations')

@app.route('/')
def default_route():
    return 'API reachable following the pattern /api/v1/*'

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    DEFAULT_PORT = 8080
    httpd = make_server('0.0.0.0', DEFAULT_PORT, app)
    httpd.serve_forever()
