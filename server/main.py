import json

from flask import Flask, Response, request, send_from_directory
app = Flask(__name__, static_url_path='')

@app.route("/helloworld")
def hello():
    return "Hello World!" 


#input coordinates are from where we want to start our heat-map in all different directions
@app.route("/map/<float:latitude>/<float:longitude>")
def index(latitude, longitude): 
    map = { 
            "stations" : [ 
                    { "uid" : "1", "name" : "Aeschenplatz", "longitude" : "47.551430", "latitude" : "7.595150", "traveltime" : 0},
                    { "uid" : "2", "name" : "Basel SBB", "longitude" : "47.548418", "latitude" : "7.590301", "traveltime" : 5}
                ],
            "connections" : [
                    { "start_uid" : "1", "end_uid" : "2"}
                ]
        }
    return Response(json.dumps(map),  mimetype='application/json')

