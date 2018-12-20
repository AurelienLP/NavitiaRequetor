# navitiaStatistics

The goal of this project is to create statistics from a list of requests launch in navitia.

# Requestor.py

Read a csv file to build some journey requests and lauch them. Store each response in a .json file and save it the output directory given in argument.

The command to use it is :

python Requestor.py serverIpAdress port coverage inputCsvFilePath outputDirectory

# ResponseParser.py

This program will parse a list of json file containing the response of a journey
It will then write 3 csv files :

    - request.csv listing for each journey of a request and for each mode
        the time, distance, number of transit and number of journey

    - journeyValueByRequestAndMode.csv regrouping all journeys of a request by mode and computing
        the mean of distance and time, the standard deviation of distance and time and the sum of transit and journey

    - mode.csv regrouping all modes

The command to use it is :

python ResponseParser.py -i inputDirectory -o outputDirectory -f coverage