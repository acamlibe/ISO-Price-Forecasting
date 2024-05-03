import requests
import sys
import csv
import time
import os
import configparser
import pytz

from datetime import datetime, timedelta
from dateutil import parser
from requests.adapters import HTTPAdapter, Retry

data_dir_exists = os.path.exists('Data/Prices')

if not data_dir_exists:
    os.mkdir('Data/Prices')

config = configparser.ConfigParser()
config.sections()

config.read('config.ini')

username = config['iso.credentials']['Username']
password = config['iso.credentials']['Password']

retries = Retry(total=5, backoff_factor=1, status_forcelist=[ 502, 503, 504, 429 ])

session = requests.Session()
session.mount('https://', HTTPAdapter(max_retries=retries))
session.headers['Accept'] = 'application/json'
session.auth = (username, password)

begin_date_arg = sys.argv[1]
end_date_arg = sys.argv[2]

begin_date = datetime.strptime(begin_date_arg, '%Y%m%d')
end_date = datetime.strptime(end_date_arg, '%Y%m%d')
delta = timedelta(days=1)

location_id = 4227

location_name = 'MASHPEE'
date = begin_date

local = pytz.timezone("America/New_York")

with open(f'Data/{location_name}.csv', 'w') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(['date', 'energy'])
    
    while date <= end_date:
        date_str = date.strftime('%Y%m%d')
        lmp_url = f'https://webservices.iso-ne.com/api/v1.1/hourlylmp/da/final/day/{date_str}/location/{location_id}'
        prices_r = session.get(lmp_url)

        if prices_r.status_code != 200:
            print(f'Error Status Code{prices_r.status_code}')
            print(prices_r.text)
            sys.exit(0)

        lmps = prices_r.json()['HourlyLmps']['HourlyLmp']
        
        last_date = None
        
        for lmp in lmps:
            hour_date_str = lmp['BeginDate']
            hour_date = parser.parse(hour_date_str)
            # to account for day light savings, duplicate hours issue.
            if last_date is not None and hour_date.hour == last_date.hour:
                continue
            energy_component = lmp['EnergyComponent']

            new_hour_date_str = hour_date.strftime('%Y-%m-%dT%H:%M:%S')
            
            csv_writer.writerow([new_hour_date_str, energy_component])
            last_date = hour_date

        last_date = date
        date += delta
        print(f'Downloaded {location_name} (ID = {location_id}) LMP data for {date_str}')
        time.sleep(0.1)