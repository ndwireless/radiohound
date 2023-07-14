#!/usr/bin/python3
'''
Downloads all scan data for given node and date range.  Scans are saved as individual json files in a directory named 'output'.
You will need to contact ND staff to be allowed through the firewall.

Author: Randy Herban @ Notre Dame
'''
import paho.mqtt.client as mqtt
import queue
import argparse
import time
import simplejson as json
import numpy
import base64
import ipaddress
import requests

parser = argparse.ArgumentParser(description='RadioHound Scan')
parser.add_argument('--node', type=str)
parser.add_argument('--start_date', type=str, help='YYYY-MM-DDTHH:MM:SS')
parser.add_argument('--end_date', type=str, help='YYYY-MM-DDTHH:MM:SS')
args = parser.parse_args()

api = f'http://radiohound.ee.nd.edu:5000/archive?node_id={args.node}&start_date={args.start_date}&end_date={args.end_date}'
results = requests.get(api).json()
for result in results:
    data_id = result['data_id']
    fmin = result['fmin']
    mac_address = result['mac_address']
    timestamp = result['timestamp'].replace(' ', '_')
    #ip_address = result['IP_addr'].replace('192.168.7.2','').replace('192.168.6.2','').rstrip().split(' ')[0]
    print(f"Found scan {data_id} {timestamp}")
    data_request = f'http://radiohound.ee.nd.edu:5000/data?id={data_id}'
    data = requests.get(data_request).json()
    print(f"Data: {data}")
    file = open(f"output/{data_id}-{mac_address}-{timestamp}.json",'w')
    file.write(json.dumps(data))
    file.close()

