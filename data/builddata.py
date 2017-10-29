import getopt
import sys
import os

from pymongo import MongoClient
import csv
import requests
import xml.etree.ElementTree as ET

#from lxml import etree
from datetime import datetime
from datetime import timedelta

from geoconv2 import GPSConverter2

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


print("string import for file: " + inputFile)

converter = GPSConverter2()

class Station:
     def __init__(self, uid, name, longitude, latitude):
         self.uid = uid
         self.name = name
         self.longitude = longitude
         self.latitude = latitude


client = MongoClient()
db = client['PubTransViz']

stations = db.stations
lines = db.lines
connections = db.connections

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


#******************************************************************************
# write stations
majorStations = []



with open(inputFile, 'r') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        # longitude = row['Y-Koord.']
        # latitude = row['X-Koord.']

        converted_coord = converter.CH1903toWGS1984(
            float(row['X-Koord.'].replace(',', '')),
            float(row['Y-Koord.'].replace(',', '')))
        #longitude = longitude[0]
        #latitude = converted[1]

        #print (converted_coord)


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
            majorStations.append(station)


teststation = majorStations[0]


# make a test-request for that given station
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
                                <NumberOfResults>2</NumberOfResults>
                                <StopEventType>departure</StopEventType>
                                <IncludePreviousCalls>true</IncludePreviousCalls>
                                <IncludeOnwardCalls>true</IncludeOnwardCalls>
                                <IncludeRealtimeData>false</IncludeRealtimeData>
                            </Params>
                        </StopEventRequest>
                    </RequestPayload>
                </ServiceRequest>
            </Trias>'''

    headers = {'Content-Type': 'application/xml', 'Authorization' : '57c5dbbbf1fe4d00010000189db17b8e65cf45027f3bd01df4eabfbe'} # set what your server accepts
    response = requests.post(url, data=xml, headers=headers)
    return response

# Parsing xml string
#root = ET.fromstring(getStops(teststation).content)

#for el in root.findall('{http://www.vdv.de/trias}OnwardCall'):
    #for sub in el:
        #if not sub.text is None:
            #if (len(sub.text.strip()) > 0):
                #print (sub.tag.split('}')[1])
                #print (sub.text)
            #for sub2 in sub:
                #if len(sub2.text.strip()) > 0:
                    #print (sub2.tag.split('}')[1])
                    #print (sub2.text)
                #for sub3 in sub2:
                    #if len(sub3.text.strip()) > 0:
                        #print (sub3.tag.split('}')[1])
                        #print (sub3.text)
                    #for sub4 in sub3:
                        #if len(sub4.text.strip()) > 0:
                            #print (sub4.tag.split('}')[1])
                            #print (sub4.text)
        #else:
            ##here we should
            #stops = sub.findall('StopEventResponse')
            #for stop in stops:
                #print(stop.text)





def parseToDatetime(string_date):
    return datetime.strptime(string_date, "%Y-%m-%dT%H:%M:%SZ")

def tryPopulateDbFromXML(xml_data):
    root = ET.fromstring(xml_data)
    # iterate result tree
    for el in root.findall('{http://www.vdv.de/trias}ServiceDelivery'):
        for deliveryPayloadElement in el.findall('{http://www.vdv.de/trias}DeliveryPayload'):
            for stopEventResponseElement in deliveryPayloadElement.findall('{http://www.vdv.de/trias}StopEventResponse'):
                for stopEventResultElement in stopEventResponseElement.findall('{http://www.vdv.de/trias}StopEventResult'):
                    for stopEventElement in stopEventResultElement.findall('{http://www.vdv.de/trias}StopEvent'):
                        #This is the level we are interessted in, first we want to grab the destination time
                        thisCallElement = stopEventElement.find('{http://www.vdv.de/trias}ThisCall')
                        thisCall_callAtStopElement = thisCallElement.find('{http://www.vdv.de/trias}CallAtStop')
                        thisCall_callAtStop_serviceDepatureElement = thisCall_callAtStopElement.find('{http://www.vdv.de/trias}ServiceDeparture')
                        thisCall_callAtStop_serviceDepature_timetabledTimeElement = thisCall_callAtStop_serviceDepatureElement.find('{http://www.vdv.de/trias}TimetabledTime')
                        departure_time = parseToDatetime(thisCall_callAtStop_serviceDepature_timetabledTimeElement.text)

                        thisCall_callAtStop_stopPointRefElement = thisCall_callAtStopElement.find('{http://www.vdv.de/trias}StopPointRef')
                        departueStationUid = thisCall_callAtStop_stopPointRefElement.text
                        print("departure station: " + departueStationUid)
                        print("departure time: " + str(departure_time))

                        #we grab the lne number
                        serviceElement = stopEventElement.find('{http://www.vdv.de/trias}Service')
                        servicee_publishedLineNameElement = serviceElement.find('{http://www.vdv.de/trias}PublishedLineName')
                        servicee_publishedLineName_textElement = servicee_publishedLineNameElement.find('{http://www.vdv.de/trias}Text')

                        #look whether we have the line already in the database, if not add it
                        lineNumber = servicee_publishedLineName_textElement.text

                        if(lineNumber is not None):
                            if(lines.find({"number": lineNumber}).count() is 0):
                                line = {
                                    "number" : lineNumber
                                }
                                lines.insert_one(line)
                                #print("added new line: " + lineNumber)

                        departureStation = stations.find_one({'uid' : departueStationUid})
                        departureStationId = departureStation['_id']

                        arrivalTime_before = departure_time
                        for onwardCallElement in stopEventElement.findall('{http://www.vdv.de/trias}OnwardCall'):
                            for callAtStopElement in onwardCallElement.findall('{http://www.vdv.de/trias}CallAtStop'):

                                stopPointRefElement = callAtStopElement.find('{http://www.vdv.de/trias}StopPointRef')
                                arrival_station_uid = stopPointRefElement.text

                                serviceArrivalElemen = callAtStopElement.find('{http://www.vdv.de/trias}ServiceArrival')
                                serviceArrival_timetabledTimeElement = serviceArrivalElemen.find('{http://www.vdv.de/trias}TimetabledTime')
                                arrival_time = parseToDatetime(serviceArrival_timetabledTimeElement.text)
                                #print("arrival: " + str(arrival_time))

                                arrivalStation = stations.find_one({'uid' : arrival_station_uid})

                                if(arrivalStation is None):
                                    break

                                #look whether we already have this connection
                                connections_in_db = connections.find({'start_station_uid' : departueStationUid, 'end_station_uid' : arrival_station_uid})
                                if(connections_in_db.count() is 0):
                                    travel_time = arrival_time - arrivalTime_before
                                    travel_time_string = str(travel_time)
                                    connection = {
                                        'start_station_uid' : departueStationUid,
                                        'start_station_id' : departureStationId,
                                        'start_station_coordinate' : departureStation['coordinates'],
                                        'end_station_uid' : arrival_station_uid,
                                        'end_station_id' : arrivalStation['_id'],
                                        'end_station_coordinate' : arrivalStation['coordinates'],
                                        'travel_time' : travel_time_string
                                        }
                                    connections.insert_one(connection)
                                    print("added new connection: " + departueStationUid + ' - ' + arrival_station_uid)

                                arrivalTime_before = arrival_time


xml_data = getStops(teststation).content
tryPopulateDbFromXML(xml_data)
