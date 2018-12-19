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

def parseArguments():
    parser = argparse.ArgumentParser(description='Optional app description')
    parser.add_argument("-i", "--inputDirectory", dest="inputDirectory", required=True,
                    help="Input directory containing all json responses", metavar="INPUT")
    parser.add_argument("-o", "--outputDirectory", dest="outputDirectory", required=True,
                    help="Output Directory", metavar="OUTPUT DIRECTORY")
    parser.add_argument("-f", "--outputFileName", dest="outputFileName", required=True,
                    help="Output File name", metavar="OUTPUT FILE")
    return parser.parse_args()

def setupLogger(outputDirectory):
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s',
                                  '%d/%m/%Y %H:%M:%S')

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    fh = logging.FileHandler( os.path.join(outputDirectory, 'responseParser.log'), 'w' )
    ch = logging.StreamHandler(sys.stdout)
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

def computeStatistics(args):
    tempcsvFilePath = args.outputDirectory + "journeyValueByRequestAndMode.csv"

    logging.info('Creating file : ' + tempcsvFilePath)
    with open(tempcsvFilePath, 'w') as csv_file:
        writer = csv.writer(csv_file, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(['requestId', 'journeyId', 'mode', 'distance', 'time', 'nbTransit', 'nbJourney'])
        for filename in os.listdir(args.inputDirectory):
            if filename.endswith(".json"):
                parseJsonFile(args.inputDirectory, filename, writer)
                continue
            else:
                continue
    
    logging.info('File ' + tempcsvFilePath + ' created !')
    logging.info('Starting pivot...')
    pivotTable(tempcsvFilePath, args.outputDirectory, args.outputFileName)
    logging.info('End pivot !')

def parseJsonFile(inputDirectory, filename, writer):
    with open(inputDirectory + '/' + filename) as f:
        data = json.load(f)
    
    journeyId = 0
    for journey in data['journeys']:
        journeyId += 1
        journeyValues = parseJourneyValues(journey)

        for mode, data in journeyValues.iteritems():
            writer.writerow([filename, journeyId, mode, data['distance'], data['time'], data['nbTransit'], data['nbJourney']]) 

def parseJourneyValues(journey):
        journeyValues = {
            'walking' : {'time' : 0, 'distance' : 0, 'nbTransit' : 0, 'nbJourney' : 0},
            'car' :     {'time' : 0, 'distance' : 0, 'nbTransit' : 0, 'nbJourney' : 0},
            'rail' :    {'time' : 0, 'distance' : 0, 'nbTransit' : 0, 'nbJourney' : 0},
            'subway' :  {'time' : 0, 'distance' : 0, 'nbTransit' : 0, 'nbJourney' : 0},
            'bus' :     {'time' : 0, 'distance' : 0, 'nbTransit' : 0, 'nbJourney' : 0},
            'waiting' : {'time' : 0, 'distance' : 0, 'nbTransit' : 0, 'nbJourney' : 0}
        }

        for section in journey['sections']:
            parseTime(journeyValues, section)
            parseDistance(journeyValues, section)
            parseNbTransit(journeyValues, section)
            parseNbJourney(journeyValues, section)

        return journeyValues

def parseTime(journeyValues, section):
    sectionType = section['type']
    sectionDuration = section['duration']

    if(sectionType == 'street_network'):
        sectionMode = section['mode']
        if (sectionMode == 'walking' or sectionMode == 'car'):
            journeyValues[sectionMode]['time'] += sectionDuration
        else:
            print('parseTime - mode inconnu : ' + sectionMode)

    elif(sectionType == 'crow_fly'):
        sectionMode = section['mode']
        if (sectionMode == 'walking' or sectionMode == 'car'):
            journeyValues[sectionMode]['time'] += sectionDuration
        else:
            print('parseTime - mode inconnu : ' + sectionMode)

    elif (sectionType == 'transfer'):
        sectionTransferType = section['transfer_type']
        if (sectionTransferType == 'walking' or sectionTransferType == 'car'):
            journeyValues[sectionTransferType]['time'] += sectionDuration
        else:
            print('parseTime - mode inconnu : ' + sectionTransferType)

    elif(sectionType == 'leave_parking' or sectionType == 'park'):
        journeyValues['car']['time'] += sectionDuration

    elif(sectionType == 'public_transport'):
        sectionCommercialMode = section['display_informations']['commercial_mode']
        if(sectionCommercialMode == 'Métro'.decode('utf-8')):
            journeyValues['subway']['time'] += sectionDuration
        elif(sectionCommercialMode == 'RER' or sectionCommercialMode == 'Tramway'):
            journeyValues['rail']['time'] += sectionDuration
        elif(sectionCommercialMode == 'Bus'):
            journeyValues['bus']['time'] += sectionDuration
        else:
            print('parseTime - Unknown commercial mode : ' + sectionCommercialMode)

    elif(sectionType == 'waiting'):
        journeyValues[sectionType]['time'] += sectionDuration

    else:
        print('parseTime - type inconnu : ' + sectionType)

def parseDistance(journeyValues, section):
    sectionType = section['type']
    sectionLength = 0

    if(sectionType == 'street_network'):
        sectionMode = section['mode']
        if (sectionMode == 'walking' or sectionMode == 'car'):
            for path in section['path']:
                sectionLength += path['length']
            journeyValues[sectionMode]['distance'] += sectionLength
        else:
            print('mode inconnu : ' + sectionMode)

    elif(sectionType == 'crow_fly'):
        sectionMode = section['mode']
        if (sectionMode == 'walking' or sectionMode == 'car'):
            pointFrom = getCoords(section, 'from')
            pointTo = getCoords(section, 'to')
            #(lat, lon)
            sectionLength = geopy.distance.distance(pointFrom, pointTo).m * 1.1
            journeyValues[sectionMode]['distance'] += sectionLength
        else:
            print('parseDistance - mode inconnu : ' + sectionMode)
    
    elif (sectionType == 'transfer'):
        sectionTransferType = section['transfer_type']
        if (sectionTransferType == 'walking' or sectionTransferType == 'car'):
            sectionLength = section['geojson']['properties'][0]['length']
            journeyValues[sectionTransferType]['distance'] += sectionLength
        else:
            print('mode inconnu : ' + sectionTransferType)

    elif(sectionType == 'public_transport'):
        sectionCommercialMode = section['display_informations']['commercial_mode']
        sectionLength = section['geojson']['properties'][0]['length']
        if(sectionCommercialMode == 'Métro'.decode('utf-8')):
            journeyValues['subway']['distance'] += sectionLength
        elif(sectionCommercialMode == 'RER' or sectionCommercialMode == 'Tramway'):
            journeyValues['rail']['distance'] += sectionLength
        elif(sectionCommercialMode == 'Bus'):
            journeyValues['bus']['distance'] += sectionLength
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

def parseNbTransit(journeyValues, section):
    sectionType = section['type']
    if(sectionType == 'public_transport'):
        sectionCommercialMode = section['display_informations']['commercial_mode']
        sectionLength = section['geojson']['properties'][0]['length']
        if(sectionCommercialMode == 'Métro'.decode('utf-8')):
            journeyValues['subway']['nbTransit'] += 1
        elif(sectionCommercialMode == 'RER' or sectionCommercialMode == 'Tramway'):
            journeyValues['rail']['nbTransit'] += 1
        elif(sectionCommercialMode == 'Bus'):
            journeyValues['bus']['nbTransit'] += 1
        else:
            print('parseNbTransit - Unknown commercial mode : ' + sectionCommercialMode)

    elif (sectionType == 'crow_fly'):
        if not(section['mode'] == 'car' or section['mode'] == 'walking'):
            print('parseNbTransit - crow_fly : ' + section['mode'])
            
    else:
        if (sectionType != 'park' and sectionType != 'waiting'
            and sectionType != 'street_network' and sectionType != 'transfer'):
            print('parseNbTransit - type inconnu : ' + sectionType)

def parseNbJourney(journeyValues, section):
    sectionType = section['type']
    sectionLength = 0

    if(sectionType == 'street_network' or sectionType == 'crow_fly'):
        sectionMode = section['mode']
        if (sectionMode == 'walking' or sectionMode == 'car'):
            journeyValues[sectionMode]['nbJourney'] = 1
        else:
            print('parseNbJourney - mode inconnu : ' + sectionMode)

    elif (sectionType == 'transfer'):
        sectionTransferType = section['transfer_type']
        if (sectionTransferType == 'walking' or sectionTransferType == 'car'):
            journeyValues[sectionTransferType]['nbJourney'] = 1
        else:
            print('parseNbJourney - mode inconnu : ' + sectionTransferType)

    elif(sectionType == 'public_transport'):
        sectionCommercialMode = section['display_informations']['commercial_mode']
        if(sectionCommercialMode == 'Métro'.decode('utf-8')):
            journeyValues['subway']['nbJourney'] = 1
        elif(sectionCommercialMode == 'RER' or sectionCommercialMode == 'Tramway'):
            journeyValues['rail']['nbJourney'] = 1
        elif(sectionCommercialMode == 'Bus'):
            journeyValues['bus']['nbJourney'] = 1
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
    convertJourneyValues(tableByRequest)
    tableByRequestFilePath = outputDirectory + 'request' + outputFileName + '.csv'
    tableByRequest.to_csv(tableByRequestFilePath)
    logging.info('File : ' + tableByRequestFilePath + ' created')

    tableByMode = pd.pivot_table(df,index=["mode"],values=["distance", "time", "nbJourney"],
                            aggfunc={"distance":[numpy.mean, numpy.std],
                                     "time":[numpy.mean, numpy.std],
                                     "nbJourney":sum})
    convertJourneyValues(tableByMode)
    tableByModeFilePath = outputDirectory + 'mode' + outputFileName + '.csv'
    tableByMode.to_csv(tableByModeFilePath)
    logging.info('File : ' + tableByModeFilePath + ' created')

def convertJourneyValues(table):
    table['distance'] = numpy.round(table['distance'] / 1000.0, 2)
    table['time'] = numpy.round( (table['time'] / 60.0), 2 )

def main():
    args = parseArguments()
    setupLogger(args.outputDirectory)
    computeStatistics(args)

main()