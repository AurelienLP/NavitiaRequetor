# coding=utf-8

import os
import sys
import csv
import statistics
import json

def parseJsonFile(filename, requestId, writer):
    with open(filename) as f:
        data = json.load(f)
    
    timeAndDistanceList = []
    journeyId = 0
    for journey in data['journeys']:
        journeyId += 1
        timeAndDistance = parseTimeAndDistance(journey)
        timeAndDistanceList.append(timeAndDistance)

        writer.writerow([requestId, journeyId, 'walking', timeAndDistance['walking']['distance'], timeAndDistance['walking']['time']])
        writer.writerow([requestId, journeyId, 'car', timeAndDistance['car']['distance'], timeAndDistance['car']['time']])
        writer.writerow([requestId, journeyId, 'rail', timeAndDistance['rail']['distance'], timeAndDistance['rail']['time']])
        writer.writerow([requestId, journeyId, 'subway', timeAndDistance['subway']['distance'], timeAndDistance['subway']['time']])
        writer.writerow([requestId, journeyId, 'bus', timeAndDistance['bus']['distance'], timeAndDistance['bus']['time']])
        writer.writerow([requestId, journeyId, 'waiting', timeAndDistance['waiting']['distance'], timeAndDistance['waiting']['time']])
    


def parseTimeAndDistance(journey):
        timeAndDistance = {
            'walking' : {'time' : 0, 'distance' : 0},
            'car' :     {'time' : 0, 'distance' : 0},
            'rail' :    {'time' : 0, 'distance' : 0},
            'subway' :  {'time' : 0, 'distance' : 0},
            'bus' :     {'time' : 0, 'distance' : 0},
            'waiting' : {'time' : 0, 'distance' : 0}
        }

        for section in journey['sections']:
            parseTime(timeAndDistance, section)
            parseDistance(timeAndDistance, section)

        return timeAndDistance

def parseTime(timeAndDistance, section):
    sectionType = section['type']
    sectionDuration = section['duration']

    if(sectionType == 'street_network'):
        sectionMode = section['mode']
        if (sectionMode == 'walking' or sectionMode == 'car'):
            timeAndDistance[sectionMode]['time'] += sectionDuration
        else:
            print('mode inconnu : ' + sectionMode)

    elif (sectionType == 'transfer'):
        sectionTransferType = section['transfer_type']
        if (sectionTransferType == 'walking' or sectionTransferType == 'car'):
            timeAndDistance[sectionTransferType]['time'] += sectionDuration
        else:
            print('mode inconnu : ' + sectionTransferType)

    elif(sectionType == 'leave_parking' or sectionType == 'park'):
        timeAndDistance['car']['time'] += sectionDuration

    elif(sectionType == 'public_transport'):
        sectionCommercialMode = section['display_informations']['commercial_mode']
        if(sectionCommercialMode == 'Métro'.decode('utf-8')):
            timeAndDistance['subway']['time'] += sectionDuration
        elif(sectionCommercialMode == 'RER'):
            timeAndDistance['rail']['time'] += sectionDuration
        elif(sectionCommercialMode == 'Bus'):
            timeAndDistance['bus']['time'] += sectionDuration
        else:
            print('Unknown commercial mode : ' + sectionCommercialMode)

    elif(sectionType == 'waiting'):
        timeAndDistance[sectionType]['time'] += sectionDuration

    else:
        print('type inconnu : ' + sectionType)

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
        elif(sectionCommercialMode == 'RER'):
            timeAndDistance['rail']['distance'] += sectionLength
        elif(sectionCommercialMode == 'Bus'):
            timeAndDistance['bus']['distance'] += sectionLength
        else:
            print('Unknown commercial mode : ' + sectionCommercialMode)
            
    else:
        if (sectionType != 'park' and sectionType != 'waiting'):
            print('type inconnu : ' + sectionType)

def main():
    inputDirectory = os.path.realpath('../data/references')
    outputDirectory = os.path.realpath('../data/statistics')
    with open(outputDirectory + '/dict.csv', 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['requestId', 'journeyId', 'mode', 'distance', 'time'])
        requestId = 0
        for filename in os.listdir(inputDirectory):
            if filename.endswith(".json"):
                requestId += 1
                parseJsonFile(inputDirectory + '/' + filename, requestId, writer)
                continue
            else:
                continue

main()