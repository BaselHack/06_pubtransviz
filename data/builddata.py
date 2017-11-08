import getopt
import sys
import os

from pymongo import MongoClient, GEO2D
import csv
import requests
import xml.etree.ElementTree as ET

from datetime import datetime, timedelta

from geoconv2 import GPSConverter2

from progressbar import AnimatedMarker, Bar, BouncingBar, Counter, ETA, \
    FileTransferSpeed, FormatLabel, Percentage, \
    ProgressBar, ReverseBar, RotatingMarker, \
    SimpleProgress, Timer, AdaptiveETA, AdaptiveTransferSpeed

#******************************************************************************
# parse input params
try:
    opts, args = getopt.getopt(sys.argv[1:], "hi:", ["help"])
except getopt.GetoptError as err:
    # print help information and exit:
    print("ERROR:")
    print(err) # will print something like "option -a not recognized"
    print("\n")
    #usage()
    sys.exit(2)
#******************************************************************************

#******************************************************************************
# usage
def usage():
    print("builddata.py version 0.1")
    print("Required options:")
    print("\t-i arg : csv file of stations")


#******************************************************************************
# define variables
inputFile = ""

#******************************************************************************
# parsing input parameters
for o, a in opts:
    if o in ("-i"):
        inputFile = a
    elif o in ("-h", "--help"):
        usage()
        sys.exit()
    else:
        assert False, "unhandled option: " + o

#******************************************************************************
# check we have everyting
if(inputFile is ""):
    print("Missing some options. Use -h to learn which options are required")
    sys.exit(2)


print("Importing data from file: " + inputFile)

converter = GPSConverter2()

#******************************************************************************
# prepare database

client = MongoClient()
db = client['PubTransViz']

# collections
stations = db.stations
lines = db.lines
connections = db.connections

# define autoincrement for index
# (we use this when we read data)
def autoincrement(name):
   ret = db.counter.find_and_modify(
       query={"_id": name},
       update={"$inc":{"seq": 1}},
       )
   return ret['seq']

if(not 'counter' in db.collection_names()):
    db.counter.insert({
    "_id": 'stations_autoincid',
    "seq": 0
    })

# make sure we have a geo-index for the coordinates
stations.create_index([("coordinates", GEO2D)])


#******************************************************************************
# collection stations from csv file
linegenstations = []

with open(inputFile, 'r') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    for row in reader:

        # convert coordinate to normal longitude,lattitude format
        converted_coord = converter.CH1903toWGS1984(
            float(row['X-Koord.'].replace(',', '')),
            float(row['Y-Koord.'].replace(',', '')))

        name = row['Name']
        uid = row['Dst-Nr85']
        station = None
        if(stations.find({"uid": uid}).count() is 0):

            station = {
                "_id": autoincrement('stations_autoincid'),
                "uid" : uid,
                "name" : name,
                "latitude" : converted_coord[0],
                "longitude" : converted_coord[1],
                "coordinates": [converted_coord[1],converted_coord[0]],
                "name" : name
            }
            stations.insert_one(station)
            print("added new station: " + uid)

        if(row['use4lineGen'] is "1"):
            linegenstations.append(station)


#******************************************************************************
# define some function to deal with trias web-service

# trias request url
url = 'https://api.opentransportdata.swiss/trias'

def getStops(station):
    xml = '''<?xml version="1.0" encoding="UTF-8"?>
            <Trias version="1.1" xmlns="http://www.vdv.de/trias" xmlns:siri="http://www.siri.org.uk/siri" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                <ServiceRequest>
                    <siri:RequestTimestamp>2016-06-27T13:34:00</siri:RequestTimestamp>
                    <siri:RequestorRef>EPSa</siri:RequestorRef>
                    <RequestPayload>
                        <StopEventRequest>
                            <Location>
                                <LocationRef>
                                    <StopPointRef>8500073</StopPointRef>
                                </LocationRef>
                                <DepArrTime>2017-10-27T10:00:00</DepArrTime>
                            </Location>
                            <Params>
                                <NumberOfResults>20</NumberOfResults>
                                <StopEventType>departure</StopEventType>
                                <IncludePreviousCalls>true</IncludePreviousCalls>
                                <IncludeOnwardCalls>true</IncludeOnwardCalls>
                                <IncludeRealtimeData>false</IncludeRealtimeData>
                            </Params>
                        </StopEventRequest>
                    </RequestPayload>
                </ServiceRequest>
            </Trias>'''
    if 'TRIAS_API_KEY' not in os.environ:
        print('Missing api key TRIAS_API_KEY')
        sys.exit(2)
    api_key = os.environ['TRIAS_API_KEY']
    headers = {'Content-Type': 'application/xml', 'Authorization' : api_key}
    response = requests.post(url, data=xml, headers=headers)
    return response


def parseToDatetime(string_date):
    return datetime.strptime(string_date, "%Y-%m-%dT%H:%M:%SZ")

def tryAddConnection(stations, departureCallElement, arrivalCallElement):
    # we always calcualte the time from departue to the departue on the next station
    # otherwise we would miss some time, maybe we need to add the wait time to the station in
    # the future (mind that the ThisCall item has no arrival time)

    # find departue and arrival station to see whether we already have the connection in the database
    departureCallAtStopElement = departureCallElement.find('{http://www.vdv.de/trias}CallAtStop')
    departureStopPointRefElement = departureCallAtStopElement.find('{http://www.vdv.de/trias}StopPointRef')
    departure_station_uid = departureStopPointRefElement.text

    arrivalCallAtStopElement = arrivalCallElement.find('{http://www.vdv.de/trias}CallAtStop')
    arrivalStopPointRefElement = arrivalCallAtStopElement.find('{http://www.vdv.de/trias}StopPointRef')
    arrival_station_uid = arrivalStopPointRefElement.text

    connections_in_db = connections.find({'start_station_uid' : departure_station_uid, 'end_station_uid' : arrival_station_uid})

    if(connections_in_db.count() is 0):
        # this means we do not yet have this connection in the database

        # check whether we have the stations in the database, if not abort
        departureStation = stations.find_one({'uid' : departure_station_uid})
        if(departureStation is None):
            return
        arrivalStation = stations.find_one({'uid' : arrival_station_uid})
        if(arrivalStation is None):
            return

        # now we calculate the travel time, always from departure to departure
        # (except for the last call, where there is only an arrival of course)

        departureServiceDepartureElement = departureCallAtStopElement.find('{http://www.vdv.de/trias}ServiceDeparture')
        departureServiceDepartureTimetabledTimeElement = departureServiceDepartureElement.find('{http://www.vdv.de/trias}TimetabledTime')
        departure_station_departureTime = parseToDatetime(departureServiceDepartureTimetabledTimeElement.text)

        arrivalServiceDepartureElement = arrivalCallAtStopElement.find('{http://www.vdv.de/trias}ServiceDeparture')
        if(arrivalServiceDepartureElement is not None):
            arrivalServiceDepartureTimetabledTimeElement = arrivalServiceDepartureElement.find('{http://www.vdv.de/trias}TimetabledTime')
            arrival_station_departureTime = parseToDatetime(arrivalServiceDepartureTimetabledTimeElement.text)
        else:
            # we are at the final station and of course only have an arrival
            arrivalServiceDepartureElement = arrivalCallAtStopElement.find('{http://www.vdv.de/trias}ServiceArrival')
            arrivalServiceDepartureTimetabledTimeElement = arrivalServiceDepartureElement.find('{http://www.vdv.de/trias}TimetabledTime')
            arrival_station_departureTime = parseToDatetime(arrivalServiceDepartureTimetabledTimeElement.text)

        traveltime = arrival_station_departureTime - departure_station_departureTime

        # departe coordinates with height 0
        cpy_departureStation = departureStation['coordinates']
        cpy_departureStation.append(0)

        # arrival coordinates with height 0
        cpy_arrivalStation = arrivalStation['coordinates']
        cpy_arrivalStation.append(0)

        connection = {
            'start_station_name' : departureStation['name'],
            'start_station_uid' : departure_station_uid,
            'start_station_id' : departureStation['_id'],
            'start' : cpy_departureStation,
            'end_station_name' : arrivalStation['name'],
            'end_station_uid' : arrival_station_uid,
            'end_station_id' : arrivalStation['_id'],
            'end' : cpy_arrivalStation,
            'travel_time' : str(traveltime),
            }
        connections.insert_one(connection)

        print("added new connection: " + departure_station_uid + ' - ' + arrival_station_uid)

# Parsing xml result data and populate database from it
def tryPopulateDbFromXML(xml_data):
    root = ET.fromstring(xml_data)
    # iterate result tree
    for el in root.findall('{http://www.vdv.de/trias}ServiceDelivery'):
        for deliveryPayloadElement in el.findall('{http://www.vdv.de/trias}DeliveryPayload'):
            for stopEventResponseElement in deliveryPayloadElement.findall('{http://www.vdv.de/trias}StopEventResponse'):
                for stopEventResultElement in stopEventResponseElement.findall('{http://www.vdv.de/trias}StopEventResult'):
                    for stopEventElement in stopEventResultElement.findall('{http://www.vdv.de/trias}StopEvent'):

                        # collect all station calls
                        stationCallElements = []

                        # collect all previous calls
                        for previousCallElement in stopEventElement.findall('{http://www.vdv.de/trias}PreviousCall'):
                            stationCallElements.append(previousCallElement)
                        # add the current call
                        thisCallElement = stopEventElement.find('{http://www.vdv.de/trias}ThisCall')
                        stationCallElements.append(thisCallElement)

                        for onwardCallElement in stopEventElement.findall('{http://www.vdv.de/trias}OnwardCall'):
                            stationCallElements.append(onwardCallElement)

                        numStations = len(stationCallElements)
                        for i in range(0, numStations-1):
                            departureCallElement = stationCallElements[i]
                            arrivalCallElement = stationCallElements[i+1]
                            tryAddConnection(stations, departureCallElement, arrivalCallElement)

                        # look whether we have the line already in the database, if not add it
                        serviceElement = stopEventElement.find('{http://www.vdv.de/trias}Service')
                        service_publishedLineNameElement = serviceElement.find('{http://www.vdv.de/trias}PublishedLineName')
                        service_publishedLineName_textElement = service_publishedLineNameElement.find('{http://www.vdv.de/trias}Text')

                        lineNumber = service_publishedLineName_textElement.text

                        if(lineNumber is not None):
                            if(lines.find({"number": lineNumber}).count() is 0):
                                line = {
                                    "number" : lineNumber
                                }
                                lines.insert_one(line)
                                print("added new line: " + lineNumber)

#******************************************************************************
# do import (with a nice progress bar of course ;-)

num_linegenstations = len(linegenstations)
print("Number of stations used for line generation: " + str(num_linegenstations))
progressBar = ProgressBar(widgets=['stations: ', Counter() , ' ',Percentage(), Bar(), ETA()], maxval=num_linegenstations).start()
progress = 0

for linegenstation in linegenstations:
    xml_data = getStops(linegenstation).content
    tryPopulateDbFromXML(xml_data)
    progress = progress + 1
    progressBar.update(progress)

progressBar.finish()
print("Importing finished")
