#!/usr/bin/env python3
'''
Downloads all scan data for given node or experiment and date range.  You will need to contact ND staff to be allowed through the firewall.

python3 get_archive_data.py --node (MAC_ADDRESS|EXPERIMENT_ID) --start_date 'YYYY-MM-DD HH:MM:SS' --end_date 'YYYY-MM-DD HH:MM:SS'

The mac address can be specified with or without colons and they'll be automatically stripped off.  
Experiqment ID will be in the form of "experiment_NNNN" with the numeric ID from the website.  
Dates can also be specified as: YYYY-MM-DD or YYYY-MM-DD HH:MM.  

Scans are saved as individual json files in a directory named 'output'.  To understand the format, look at the parse_scan.py file in this repository.  

Author: Randy Herban @ Notre Dame
'''
import paho.mqtt.client as mqtt
import argparse
import simplejson as json
import requests
import os
import sys
import re

parser = argparse.ArgumentParser(description='RadioHound Scan')
parser.add_argument('--node', type=str, help="Mac address of the target node, with or without colons.  Or Experiment ID: experiment_NNNN")
parser.add_argument('--start_date', type=str, help='YYYY-MM-DD HH:MM:SS')
parser.add_argument('--end_date', type=str, help='YYYY-MM-DD HH:MM:SS')
args = parser.parse_args()
if not os.path.isdir('output'):
  os.mkdir('output')

args.node = args.node.replace(':', '')
args.start_date = args.start_date.replace(' ', 'T')
args.end_date = args.end_date.replace(' ', 'T')
# Auto-append time if not entered
if re.match("\d{4}-\d{2}-\d{2}$", args.start_date):
    args.start_date += "T00:00:00"
if re.match("\d{4}-\d{2}-\d{2}T00$", args.start_date):
    args.start_date += ":00:00"
if re.match("\d{4}-\d{2}-\d{2}T00:00$", args.start_date):
    args.start_date += ":00"
if re.match("\d{4}-\d{2}-\d{2}$", args.end_date):
    args.end_date += "T23:59:00"
if re.match("\d{4}-\d{2}-\d{2}T00$", args.end_date):
    args.end_date += ":00:00"
if re.match("\d{4}-\d{2}-\d{2}T00:00$", args.end_date):
    args.end_date += ":00"


try:
    api = f'http://radiohound.ee.nd.edu:5000/archive?node_id={args.node}&start_date={args.start_date}&end_date={args.end_date}'
    results = requests.get(api).json()
except:
    print(f"Error requesting data from server\n{api}")
    sys.exit(1)

for result in results:
    try:
        data_id = result['data_id']
        fmin = result['fmin']
        timestamp = result['timestamp'].replace(' ', '_').replace(':','').split('.')[0] # replace colons, spaces and trim off the milliseconds
        print(f"Found scan {data_id} {timestamp}")
        data_request = f'http://radiohound.ee.nd.edu:5000/data?id={data_id}'
        data = requests.get(data_request).json()
        mac_address = data['mac_address']
        #print(f"Data: {data}")
        file = open(f"output/{data_id}-{mac_address}-{timestamp}.json",'w')
        file.write(json.dumps(data))
        file.close()
    except Exception as e:
        print(f":{e}\nData was: {result}")

