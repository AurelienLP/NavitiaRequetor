# coding=utf-8

import os
import requests
import csv
import codecs
import argparse

def main():

    parser = argparse.ArgumentParser(description='Optional app description')
    parser.add_argument('ipAdress', help='Ip adress of the Jormungandr server')
    parser.add_argument('port', help='Port of the Jormungandr server')
    parser.add_argument('coverage', help='Coverage used in the request')
    parser.add_argument('inputFile', help='Input csv file containing the requests to parse')
    parser.add_argument('outputDirectory', help='Output directory which will contain all the json response file')
    
    args = parser.parse_args()

    input_file = csv.DictReader( open( args.inputFile ) )
    nbRequest = 0
    for row in input_file:
        nbRequest = nbRequest + 1
        pointFrom = row['LonFrom'] + ';' + row['LatFrom']
        pointTo = row['LonTo'] + ';' + row['LatTo']
        
        requestParameter = {'from' : pointFrom,
                            'to' : pointTo,
                            'datetime' : row['dateTime'],
                            '_override_scenario' : 'distributed',
                            'first_section_mode' : 'car',
                            'last_section_mode' : 'walking'
        }

        url = 'http://' + args.ipAdress + ':' + args.port + '/v1/coverage/' + args.coverage + '/journeys'
        r = requests.get(url, params=requestParameter)
        if(r.status_code != 200):
            print('Error with request : ' + r.url)
            continue
        
        print(r.url)

        fileName = args.outputDirectory + '/' + row['Description'] + str(nbRequest) + '.json'
        print(fileName)
        f = codecs.open(fileName, "w+", 'utf-8')
        f.write(r.text)
        f.close()

main()