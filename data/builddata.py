
import getopt
import sys
import os

from pymongo import MongoClient

import csv

import requests
from xml.etree import ElementTree


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


class Station:
     def __init__(self, uid, name, longitude, latitude):
        self.uid = uid
        self.name = name
        self.longitude = longitude
        self.latitude = latitude
        
        



client = MongoClient()
db = client['PubTransViz']

stations = db.stations

#******************************************************************************
# write stations



majorStations = []

with open(inputFile, 'r') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        longitude = row['Y-Koord.']
        latitude = row['X-Koord.']
        name = row['Name']
        uid = row['Dst-Nr85']    
        station = {
            "uid" : uid,
            "name" : name,
            "latitude" : latitude,
            "longitude" : longitude,
            "name" : name
        }
        #station_id = stations.insert_one(station).inserted_id
        
        if(row['use4lineGen'] is "1"):
            majorStations.append(station)

        

teststation = majorStations[0]
# make a test-request for that given station

url = 'https://api.opentransportdata.swiss/trias'
def getStops(station):
    xml = """<?xml version="1.0" encoding="UTF-8"?> 
            <Trias version="1.1" xmlns="http://www.vdv.de/trias" xmlns:siri="http://www.siri.org.uk/siri" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                <ServiceRequest>
                    <siri:RequestTimestamp>2016-06-27T13:34:00</siri:RequestTimestamp>
                    <siri:RequestorRef>EPSa</siri:RequestorRef>
                    <RequestPayload>
                        <StopEventRequest>
                            <Location>
                                <LocationRef>
                                    <StopPointRef>""" + "8500010" +"""</StopPointRef>
                                </LocationRef>
                                <DepArrTime>2017-10-27T10:00:00</DepArrTime>
                            </Location>
                            <Params>
                                <NumberOfResults>200</NumberOfResults>
                                <StopEventType>departure</StopEventType>
                                <IncludePreviousCalls>true</IncludePreviousCalls>
                                <IncludeOnwardCalls>true</IncludeOnwardCalls>
                                <IncludeRealtimeData>false</IncludeRealtimeData>
                            </Params>
                        </StopEventRequest>
                    </RequestPayload>
                </ServiceRequest>
            </Trias>"""

    headers = {'Content-Type': 'application/xml', 'Authorization' : '57c5dbbbf1fe4d00010000189db17b8e65cf45027f3bd01df4eabfbe'} # set what your server accepts
    response = requests.post(url, data=xml, headers=headers)
    return response

response = getStops(teststation)
#response.raw.decode_content = True

#root = ET.fromstring(country_data_as_string)

#print(response.content)

##events = ElementTree.iterparse(response.raw)
##for event, elem in events:
    ##print(event)


tree = ElementTree.fromstring(response.content)

list = elem.xpath('//Trias')
print("result set:")
for item in list:
    field = item.getparent().getparent().attrib['k']
    value = item.text
    print("\t%s = %s"%(field, value))

