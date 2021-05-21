import sys
import codecs
import urllib.request
import urllib.parse
import time

if len(sys.argv) > 1:
    aggregateHours = sys.argv[1]
    suffix = '_hourly'
else:
    aggregateHours = '24'
    suffix = ''

locations_dict = {'32 Camino Del Diablo':'Orinda',
                  'Jamestown, CA':'Jamestown',
                  'Yosemite Village, CA':'Yosemite',
                  'Bishop, CA':'Bishop',
                  'Portland, OR':'Portland',
                  'Cincinnati, OH':'Cincinnati'}

URLbase = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/weatherdata/forecast?'

query = {'locations':'32 Camino Del Diablo',
         'aggregateHours':aggregateHours,  # 1, 12, or 24
         'forecastDays':'15',
         'combinationMethod':'aggregate',
         'contentType':'csv',  # or 'json'
         'unitGroup':'us',  # us, uk, metric, or base
         'locationMode':'single',
         'dataElements':'default',
         'shortColumnNames':'false',
         'includeAstronomy':'false',
         'key':'J4599FP7WHJXL9VM5Y6XJCP4V'}

date_string = time.strftime('%Y%m%d')

for k, v in locations_dict.items():
    query['locations'] = k

    # Build the entire query
    URL = URLbase + urllib.parse.urlencode(query)

    # Parse the results as CSV
    CSVBytes = urllib.request.urlopen(URL)

    with open(f'Forecasts{suffix}/{v}{date_string}.csv', 'w') as ff:
        for s in codecs.iterdecode(CSVBytes, 'utf-8'):
            ff.write(s)

