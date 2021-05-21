import os
import sys
import codecs
import urllib.request
import urllib.parse
import time
import pandas
import matplotlib.dates
from datetime import datetime

if len(sys.argv) > 1:
    aggregateHours = sys.argv[1]
    suffix = '_hourly'
else:
    aggregateHours = '24'
    suffix = ''

date_string = time.strftime('%Y-%m-%d')

locations_dict = {'32 Camino Del Diablo':'Orinda',
                  'Jamestown, CA':'Jamestown',
                  'Yosemite Village, CA':'Yosemite',
                  'Bishop, CA':'Bishop',
                  'Portland, OR':'Portland',
                  'Cincinnati, OH':'Cincinnati'}

URLbase = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/weatherdata/history?'


query = {'locations':'32 Camino Del Diablo',
         'aggregateHours':aggregateHours,  # 1, 12, or 24
         'unitGroup':'us',  # us, uk, metric, or base
         'contentType':'csv',  # or 'json'
         'shortColumnNames':'false',
         'includeAstronomy':'false',
         'combinationMethod':'aggregate',
         'dataElements':'default', # ??
         'startDateTime':'2021-03-11T00:00:00',
         'endDateTime':f'{date_string}T00:00:00',
         'dayStartTime':'0:0:00',
         'dayEndTime':'0:0:00',
         'key':'J4599FP7WHJXL9VM5Y6XJCP4V'}



for k, v in locations_dict.items():
    query['locations'] = k

    history_file = f'History{suffix}/{v}.csv'

    # Read up to the current data, reading at most four days
    # at a time (because of Visual Crossing acount limits)
    startdate_num = matplotlib.dates.date2num(datetime.strptime('03/11/2021', '%m/%d/%Y'))
    already_exists = os.path.exists(history_file)
    if already_exists:
        dd = pandas.read_csv(history_file)
        lastdate = dd['Date time'].to_list()[-1]
        if aggregateHours == 1:
            lastdate_num = int(matplotlib.dates.date2num(datetime.strptime(lastdate, '%m/%d/%Y %H:%M:%S')))
        else:
            lastdate_num = int(matplotlib.dates.date2num(datetime.strptime(lastdate, '%m/%d/%Y')))
        startdate_num = lastdate_num + 1

    max_days = 3*int(aggregateHours)
    enddate_num = int(matplotlib.dates.date2num(datetime.today()))
    if enddate_num > startdate_num + max_days:
        enddate_num = startdate_num + max_days
    elif startdate_num > enddate_num:
        sys.exit()

    enddate_num += 23./24.

    startdate = matplotlib.dates.num2date(startdate_num).strftime('%Y-%m-%dT%H:%M:%S')
    enddate = matplotlib.dates.num2date(enddate_num).strftime('%Y-%m-%dT%H:%M:%S')
    query['startDateTime'] = startdate
    query['endDateTime'] = enddate

    # Build the entire query
    URL = URLbase + urllib.parse.urlencode(query)

    # Parse the results as CSV
    CSVBytes = urllib.request.urlopen(URL)

    with open(f'History{suffix}/{v}.csv', 'a') as ff:
        for i,s in enumerate(codecs.iterdecode(CSVBytes, 'utf-8')):
            if s.startswith('You have exceeded the maximum number of daily result records for your account'):
                print(s)
                sys.exit()
            if i == 0:
                if not already_exists:
                    ff.write(s)
            else:
                ff.write(s)

