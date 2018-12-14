# coding=utf-8

import os
import requests
import csv
import codecs

input_file = csv.DictReader( open( os.path.realpath('../data/requests/requests.csv') ) )
outputDirectory = os.path.realpath('../data/responses')
nbRequest = 0
for row in input_file:
    nbRequest = nbRequest + 1
    pointFrom = row['LonFrom'] + ';' + row['LatFrom']
    pointTo = row['LonTo'] + ';' + row['LatTo']
    
    requestParameter = {'from' : pointFrom,
                        'to' : pointTo,
                        'dateTime' : row['dateTime'],
                        '_override_scenario' : 'distributed',
                        'first_section_mode' : 'car',
                        'last_section_mode' : 'walking'
    }

    r = requests.get('http://localhost:5000/v1/coverage/default/journeys', params=requestParameter)
    if(r.status_code != 200):
        print('Error with request : ' + requestParameter)
        continue
    
    print(r.url)

    fileName = outputDirectory + '/' + row['Description'] + str(nbRequest) + '.json'
    print(fileName)
    f = codecs.open(fileName, "w+", 'utf-8')
    f.write(r.text)
    f.close()
