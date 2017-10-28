
import getopt
import sys
import os

from pymongo import MongoClient

import csv



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
        station_id = stations.insert_one(station).inserted_id
