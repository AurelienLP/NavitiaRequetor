# coding=utf-8

import os
import sys
import csv
import statistics
import json
import pandas as pd
import numpy
import argparse
import geopy.distance

def parseJsonFile(inputDirectory, filename, writer):
    with open(inputDirectory + '/' + filename) as f:
        data = json.load(f)
    
    journeyId = 0
    for journey in data['journeys']:
        journeyId += 1
        timeAndDistance = parseTimeAndDistance(journey)

        for mode, data in timeAndDistance.iteritems():
            writer.writerow([filename, journeyId, mode, data['distance'], data['time'], data['nbTransit'], data['nbJourney']]) 

def parseTimeAndDistance(journey):
        timeAndDistance = {
            'walking' : {'time' : 0, 'distance' : 0, 'nbTransit' : 0, 'nbJourney' : 0},
            'car' :     {'time' : 0, 'distance' : 0, 'nbTransit' : 0, 'nbJourney' : 0},
            'rail' :    {'time' : 0, 'distance' : 0, 'nbTransit' : 0, 'nbJourney' : 0},
            'subway' :  {'time' : 0, 'distance' : 0, 'nbTransit' : 0, 'nbJourney' : 0},
            'bus' :     {'time' : 0, 'distance' : 0, 'nbTransit' : 0, 'nbJourney' : 0},
            'waiting' : {'time' : 0, 'distance' : 0, 'nbTransit' : 0, 'nbJourney' : 0}
        }

        for section in journey['sections']:
            parseTime(timeAndDistance, section)
            parseDistance(timeAndDistance, section)
            parseNbTransit(timeAndDistance, section)
            parseNbJourney(timeAndDistance, section)

        return timeAndDistance

def parseTime(timeAndDistance, section):
    sectionType = section['type']
    sectionDuration = section['duration']

    if(sectionType == 'street_network'):
        sectionMode = section['mode']
        if (sectionMode == 'walking' or sectionMode == 'car'):
            timeAndDistance[sectionMode]['time'] += sectionDuration
        else:
            print('parseTime - mode inconnu : ' + sectionMode)

    elif(sectionType == 'crow_fly'):
        sectionMode = section['mode']
        if (sectionMode == 'walking' or sectionMode == 'car'):
            timeAndDistance[sectionMode]['time'] += sectionDuration
        else:
            print('parseTime - mode inconnu : ' + sectionMode)

    elif (sectionType == 'transfer'):
        sectionTransferType = section['transfer_type']
        if (sectionTransferType == 'walking' or sectionTransferType == 'car'):
            timeAndDistance[sectionTransferType]['time'] += sectionDuration
        else:
            print('parseTime - mode inconnu : ' + sectionTransferType)

    elif(sectionType == 'leave_parking' or sectionType == 'park'):
        timeAndDistance['car']['time'] += sectionDuration

    elif(sectionType == 'public_transport'):
        sectionCommercialMode = section['display_informations']['commercial_mode']
        if(sectionCommercialMode == 'Métro'.decode('utf-8')):
            timeAndDistance['subway']['time'] += sectionDuration
        elif(sectionCommercialMode == 'RER' or sectionCommercialMode == 'Tramway'):
            timeAndDistance['rail']['time'] += sectionDuration
        elif(sectionCommercialMode == 'Bus'):
            timeAndDistance['bus']['time'] += sectionDuration
        else:
            print('parseTime - Unknown commercial mode : ' + sectionCommercialMode)

    elif(sectionType == 'waiting'):
        timeAndDistance[sectionType]['time'] += sectionDuration

    else:
        print('parseTime - type inconnu : ' + sectionType)

def parseDistance(timeAndDistance, section):
    sectionType = section['type']
    sectionLength = 0

    if(sectionType == 'street_network'):
        sectionMode = section['mode']
        if (sectionMode == 'walking' or sectionMode == 'car'):
            for path in section['path']:
                sectionLength += path['length']
            timeAndDistance[sectionMode]['distance'] += sectionLength
        else:
            print('mode inconnu : ' + sectionMode)

    elif(sectionType == 'crow_fly'):
        sectionMode = section['mode']
        if (sectionMode == 'walking' or sectionMode == 'car'):
            pointFrom = getCoords(section, 'from')
            pointTo = getCoords(section, 'to')
            #(lat, lon)
            sectionLength = geopy.distance.distance(pointFrom, pointTo).m * 1.1
            timeAndDistance[sectionMode]['distance'] += sectionLength
        else:
            print('parseDistance - mode inconnu : ' + sectionMode)
    

    elif (sectionType == 'transfer'):
        sectionTransferType = section['transfer_type']
        if (sectionTransferType == 'walking' or sectionTransferType == 'car'):
            sectionLength = section['geojson']['properties'][0]['length']
            timeAndDistance[sectionTransferType]['distance'] += sectionLength
        else:
            print('mode inconnu : ' + sectionTransferType)

    elif(sectionType == 'public_transport'):
        sectionCommercialMode = section['display_informations']['commercial_mode']
        sectionLength = section['geojson']['properties'][0]['length']
        if(sectionCommercialMode == 'Métro'.decode('utf-8')):
            timeAndDistance['subway']['distance'] += sectionLength
        elif(sectionCommercialMode == 'RER' or sectionCommercialMode == 'Tramway'):
            timeAndDistance['rail']['distance'] += sectionLength
        elif(sectionCommercialMode == 'Bus'):
            timeAndDistance['bus']['distance'] += sectionLength
        else:
            print('parseDistance - Unknown commercial mode : ' + sectionCommercialMode)
            
    else:
        if (sectionType != 'park' and sectionType != 'waiting'):
            print('parseDistance - type inconnu : ' + sectionType)

def getCoords(section, key):
    sectionEmbeddedType = section[key]['embedded_type']
    if sectionEmbeddedType == 'address':
        stringCoords = section[key]['id']
        splittedString = stringCoords.split(';')
        return (splittedString[1], splittedString[0])

    elif sectionEmbeddedType == 'stop_point':
        coords = section[key][sectionEmbeddedType]['coord']
        return (coords['lat'], coords['lon'])

    else:
        print('sectionEmbeddedType inconnu : ' + sectionEmbeddedType)
        return (0,0)

def parseNbTransit(timeAndDistance, section):
    sectionType = section['type']
    if(sectionType == 'public_transport'):
        sectionCommercialMode = section['display_informations']['commercial_mode']
        sectionLength = section['geojson']['properties'][0]['length']
        if(sectionCommercialMode == 'Métro'.decode('utf-8')):
            timeAndDistance['subway']['nbTransit'] += 1
        elif(sectionCommercialMode == 'RER' or sectionCommercialMode == 'Tramway'):
            timeAndDistance['rail']['nbTransit'] += 1
        elif(sectionCommercialMode == 'Bus'):
            timeAndDistance['bus']['nbTransit'] += 1
        else:
            print('parseNbTransit - Unknown commercial mode : ' + sectionCommercialMode)

    elif (sectionType == 'crow_fly'):
        if not(section['mode'] == 'car' or section['mode'] == 'walking'):
            print('parseNbTransit - crow_fly : ' + section['mode'])
            
    else:
        if (sectionType != 'park' and sectionType != 'waiting'
            and sectionType != 'street_network' and sectionType != 'transfer'):
            print('parseNbTransit - type inconnu : ' + sectionType)

def parseNbJourney(timeAndDistance, section):
    sectionType = section['type']
    sectionLength = 0

    if(sectionType == 'street_network' or sectionType == 'crow_fly'):
        sectionMode = section['mode']
        if (sectionMode == 'walking' or sectionMode == 'car'):
            timeAndDistance[sectionMode]['nbJourney'] = 1
        else:
            print('parseNbJourney - mode inconnu : ' + sectionMode)

    elif (sectionType == 'transfer'):
        sectionTransferType = section['transfer_type']
        if (sectionTransferType == 'walking' or sectionTransferType == 'car'):
            timeAndDistance[sectionTransferType]['nbJourney'] = 1
        else:
            print('parseNbJourney - mode inconnu : ' + sectionTransferType)

    elif(sectionType == 'public_transport'):
        sectionCommercialMode = section['display_informations']['commercial_mode']
        if(sectionCommercialMode == 'Métro'.decode('utf-8')):
            timeAndDistance['subway']['nbJourney'] = 1
        elif(sectionCommercialMode == 'RER' or sectionCommercialMode == 'Tramway'):
            timeAndDistance['rail']['nbJourney'] = 1
        elif(sectionCommercialMode == 'Bus'):
            timeAndDistance['bus']['nbJourney'] = 1
        else:
            print('parseNbJourney - Unknown commercial mode : ' + sectionCommercialMode)
            
    else:
        if (sectionType != 'park' and sectionType != 'waiting'):
            print('parseNbJourney - type inconnu : ' + sectionType)

def pivotTable(tempcsvFilePath, outputDirectory, outputFileName):
    df = pd.read_csv(tempcsvFilePath)

    tableByRequest = pd.pivot_table(df,index=["requestId", "mode"],values=["distance", "time", "nbTransit", "nbJourney"],
                            aggfunc={"distance":[numpy.mean, numpy.std],
                                    "time":[numpy.mean, numpy.std],
                                    "nbTransit":sum, "nbJourney":sum})
    convertTimeAndDistance(tableByRequest)
    tableByRequest.to_csv(outputDirectory + '/' + 'request' + outputFileName + '.csv')

    tableByMode = pd.pivot_table(df,index=["mode"],values=["distance", "time", "nbJourney"],
                            aggfunc={"distance":[numpy.mean, numpy.std],
                                     "time":[numpy.mean, numpy.std],
                                     "nbJourney":sum})
    convertTimeAndDistance(tableByMode)
    tableByMode.to_csv(outputDirectory + '/' + 'mode' + outputFileName + '.csv')

def convertTimeAndDistance(table):
    table['distance'] = numpy.round(table['distance'] / 1000.0, 2)
    table['time'] = numpy.round( (table['time'] / 60.0), 2 )

def main():
    parser = argparse.ArgumentParser(description='Optional app description')
    parser.add_argument("-i", "--inputDirectory", dest="inputDirectory", required=True,
                    help="Input directory containing all json responses", metavar="INPUT")
    parser.add_argument("-o", "--outputDirectory", dest="outputDirectory", required=True,
                    help="Output Directory", metavar="OUTPUT DIRECTORY")
    parser.add_argument("-f", "--outputFileName", dest="outputFileName", required=True,
                    help="Output File name", metavar="OUTPUT FILE")
    
    args = parser.parse_args()
    tempcsvFilePath = args.outputDirectory + '/' + "temp.csv"
                    
    with open(tempcsvFilePath, 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['requestId', 'journeyId', 'mode', 'distance', 'time', 'nbTransit', 'nbJourney'])
        for filename in os.listdir(args.inputDirectory):
            if filename.endswith(".json"):
                parseJsonFile(args.inputDirectory, filename, writer)
                continue
            else:
                continue
    
    pivotTable(tempcsvFilePath, args.outputDirectory, args.outputFileName)

main()