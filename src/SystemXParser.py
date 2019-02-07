# coding=utf-8

import os
import sys
import csv
import json
import pandas as pd
import numpy
import argparse
import geopy.distance
import logging

# This program will parse a list of json file containing the response of a journey
# It will then write 3 csv files :
#   - request.csv listing for each journey of a request and for each mode
#       the time, distance, number of transit and number of journey
#   - journeyValueByRequestAndMode.csv regrouping all journeys of a request by mode and computing
#       the mean of distance and time, the standard deviation of distance and time and the sum of transit and journey
#   - mode.csv regrouping all modes

def parseArguments():
    parser = argparse.ArgumentParser(description='Optional app description')
    parser.add_argument("-i", "--inputDirectory", dest="inputDirectory", required=True,
                    help="Input directory containing all json responses", metavar="INPUT")
    parser.add_argument("-o", "--outputDirectory", dest="outputDirectory", required=True,
                    help="Output Directory", metavar="OUTPUT DIRECTORY")
    # parser.add_argument("-f", "--outputFileName", dest="outputFileName", required=True,
    #                 help="Output File name", metavar="OUTPUT FILE")
    return parser.parse_args()

def setupLogger(outputDirectory):
    formatter = logging.Formatter('[%(asctime)s] [%(filename)s:%(lineno)s] [%(levelname)s] %(message)s',
                                  '%d/%m/%Y %H:%M:%S')

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    fh = logging.FileHandler( os.path.join(outputDirectory, 'systemXParser.log'), 'w' )
    ch = logging.StreamHandler(sys.stdout)
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

def parseResponse(args):
    with open(args.outputDirectory + '/' + 'journeys.csv', 'w') as csvJourneysFile:
        writer = csv.writer(csvJourneysFile, delimiter=';', lineterminator='\n')
        itinararies_names = ['id_journey', 'possible_modes', 'date', 'startTime', 'endTime', 'x_origin', 'y_origin',
                            'x_dest', 'y_dest', 'duration', 'walkTime', 'transitTime', 'waitingTime', 'walkDistance',
                            'walkLimitExceeded', 'transfers']
        writer.writerow(itinararies_names)

    with open(args.outputDirectory + '/' + 'legs.csv', 'w') as csvLegsFile:
        writer = csv.writer(csvLegsFile, delimiter=';', lineterminator='\n')
        legs_names = ['id_journey',
                        'id_leg',
                        'legMode',
                        'date',
                        'startTime',
                        'endTime',
                        'x_origin',
                        'y_origin',
                        'x_dest',
                        'y_dest',
                        'legStartTime',
                        'legEndTime',
                        'legDepartureDelay',
                        'legArrivalDelay',
                        'legDistance',
                        'legInterlineWithPreviousLeg',
                        'legDuration',
                        'legStopIdOrigin',
                        'legOrigName',
                        'x_legOrigin',
                        'y_legOrigin',
                        'legStopIdDest',
                        'legDestName',
                        'x_legDest',
                        'y_legDest',
                        'transitLeg',
                        'route',
                        'agencyName',
                        'tripshortName',
                        'headsign',
                        ]
        writer.writerow(legs_names)


    for filename in os.listdir(args.inputDirectory):
        if filename.endswith(".json"):
            with open(args.inputDirectory + '/' + filename) as f:
                data = json.load(f)
            
            date = data['journeys'][0]["requested_date_time"]
            mode = 'CAR_PARK,WALK,TRANSIT'

            href = data["links"][0]["href"]
            queryKeyValue = dict(s.split('=', 1) for s in href.split("?")[1].split("&"))
            origin = queryKeyValue["from"].split(";")
            x_origin = origin[0]
            y_origin = origin[1]

            dest = queryKeyValue["to"].split(";")
            x_dest = dest[0]
            y_dest = dest[1]

            id_journey = 1
            for journey in data['journeys']:
                duration = journey["durations"]["total"]
                startTime =  journey["departure_date_time"]
                endTime =  journey["arrival_date_time"]
                walkTime = journey["durations"]["walking"]
                transitTime = 0   # A CHANGER !!
                waitingTime = 0   # A CHANGER !
                walkDistance = journey["distances"]["walking"]
                walkLimitExceeded  = False # Equivalent dans navitia ?
                transfers  = journey["nb_transfers"]

                id_leg = 1

                for index, leg in enumerate(journey["sections"]):
                    legStartTime = leg["departure_date_time"]
                    legEndTime = leg["arrival_date_time"]
                    legDepartureDelay = 0 # What ?
                    legArrivalDelay = 0 # What ?
                    legDistance= computeLegDistance(leg)
                    legInterlineWithPreviousLeg = 0 # What ?
                    legMode = getLegMode(leg)
                    legDuration = leg["duration"]
                    
                    legType = leg["type"]
                    if legType == "waiting":
                        waitingTime += legDuration
                    elif legType == "public_transport":
                        transitTime += legDuration
                        
                    if legType != "waiting":
                        legOrigName = leg["from"]["name"].encode('utf-8')
                        legOriginCoords = getCoords(leg, "from", index)
                        x_legOrigin = legOriginCoords[1]
                        y_legOrigin = legOriginCoords[0]
                        legDestName = leg["to"]["name"].encode('utf-8')
                        legDestCoords = getCoords(leg, "from", index)
                        x_legDest = legDestCoords[1]
                        y_legDest = legDestCoords[0]
                        transitLeg = isTransitLeg(legType)

                        if 'display_informations' in leg:
                            route = leg["display_informations"]["name"].encode('utf-8')
                            agencyName = leg["display_informations"]["network"].encode('utf-8')
                            tripshortName = leg["display_informations"]["headsign"].encode('utf-8')
                            headsign = leg["display_informations"]["direction"].encode('utf-8')
                        else:
                            route = None
                            agencyName = None
                            tripshortName = None
                            headsign = None

                        if  'stop_point' in leg["from"]:
                            legStopIdOrigin=leg["from"]["stop_point"]["id"]
                        else:
                            legStopIdOrigin = None

                        if  'stop_point' in leg["to"]:
                            legStopIdDest=leg["to"]["stop_point"]["id"]
                        else:
                            legStopIdDest = None

                    else:
                        legOrigName = None
                        legOriginCoords = None
                        x_legOrigin = None
                        y_legOrigin = None
                        legDestName = None
                        legDestCoords = None
                        x_legDest = None
                        y_legDest = None
                        transitLeg = None
                        route = None
                        agencyName = None
                        tripshortName = None
                        headsign = None
                        legStopIdOrigin = None
                        legStopIdDest = None

                    row_legs = [id_journey,
                                id_leg,
                                legMode,
                                date,
                                startTime,
                                endTime,
                                x_origin,
                                y_origin,
                                x_dest,
                                y_dest,
                                legStartTime,
                                legEndTime,
                                legDepartureDelay,
                                legArrivalDelay,
                                legDistance,
                                legInterlineWithPreviousLeg,
                                legDuration,
                                legStopIdOrigin,
                                legOrigName,
                                x_legOrigin,
                                y_legOrigin,
                                legStopIdDest,
                                legDestName,
                                x_legDest,
                                y_legDest,
                                transitLeg,
                                route,
                                agencyName,
                                tripshortName,
                                headsign,
                                    ]

                    with open(args.outputDirectory + '/' + 'legs.csv', 'a') as csvLegsFile:
                        writer = csv.writer(csvLegsFile, delimiter=';',lineterminator='\n')
                        writer.writerow(row_legs)

                    id_leg += 1

                row_journeys = [id_journey,
                                mode,
                                date,
                                startTime,
                                endTime,
                                x_origin,
                                y_origin,
                                x_dest,
                                y_dest,
                                duration,
                                walkTime,
                                transitTime,
                                waitingTime,
                                walkDistance,
                                walkLimitExceeded,
                                transfers]

                with open(args.outputDirectory + '/' + 'journeys.csv', 'a') as csvJourneysFile:
                    writer = csv.writer(csvJourneysFile, delimiter=';',lineterminator='\n')
                    writer.writerow(row_journeys)

                print("******************************")
                id_journey +=1
            continue
        else:
            continue


    

    csvLegsFile.close()
    csvJourneysFile.close()

def getCoords(leg, key, index):
    if leg["type"] == "waiting":
        logging.warn('legEmbeddedType = ' + str(leg["type"]))
        return (0,0)

    legEmbeddedType = leg[key].get('embedded_type')
    if (legEmbeddedType and legEmbeddedType == 'address') or leg[key].get("address"):
        stringCoords = leg[key]['id']
        splittedString = stringCoords.split(';')
        return (splittedString[1], splittedString[0])

    elif legEmbeddedType == 'stop_point' or legEmbeddedType == 'poi':
        coords = leg[key][legEmbeddedType]['coord']
        return (coords['lat'], coords['lon'])

    else:
        logging.error('Unknown legEmbeddedType : ' + str(legEmbeddedType))
        return (0,0)

def computeLegDistance(leg):
    legType = leg['type']
    if legType == "waiting" or legType == "transfer":
        return 0

    elif legType == "public_transport" or legType == "transfer" or legType == "street_network":
        return leg["geojson"]["properties"][0]["length"]

    elif(legType == 'crow_fly'):
        legMode = leg['mode']
        if (legMode == 'walking' or legMode == 'car'):
            pointFrom = getCoords(leg, 'from', 0)
            pointTo = getCoords(leg, 'to', 0)
            #(lat, lon)
            return geopy.distance.distance(pointFrom, pointTo).m * 1.1
        else:
            logging.error('Unknown mode : ' + legMode)
    
    else:
        distance = 0
        for path in leg["path"]:
            distance += path["length"]

        return distance

def getLegMode(leg):
    legType = leg['type']

    if(legType == 'street_network' or legType == 'crow_fly'):
        if leg['mode'] == "car":
            return "CAR"
        else:
            return "WALK"
    elif(legType == "waiting" or legType == 'transfer'):
        return "WALK"
    elif(legType == "park"):
        return "CAR"

    elif(legType == 'public_transport'):
        legCommercialMode = leg['display_informations']['commercial_mode']
        print(legCommercialMode)
        if(legCommercialMode == "Rail"):
            return "RAIL"
        elif(legCommercialMode == "Subway, Metro"):
            return "SUBWAY"
        elif(legCommercialMode == 'Bus'):
            return "BUS"
    else:
        return None

def isTransitLeg(mode):
    if mode == "public_transport":
        return True
    else:
        return False

def main():
    args = parseArguments()
    setupLogger(args.outputDirectory)
    parseResponse(args)

main()
