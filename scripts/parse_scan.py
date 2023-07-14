#!/usr/bin/env python
'''
 Parses a downloaded RadioHound scan file

 Should be ran with the filename as input:
 python parse_scan.py sample.json

 Author: Randy Herban @ Notre Dame
'''
import base64
import json
import numpy
import sys

file = sys.argv[1]
with open(file,'r') as handle:
    input = json.load(handle)

dt = numpy.dtype(input["type"])
data = numpy.frombuffer(base64.b64decode(input["data"]), dtype=dt)
print("data: " + str(data))
print("len(data): " + str(len(data)))
freq_array = numpy.linspace(input['metadata']['fmin'], input['metadata']['fmax'], input['metadata']['nfft'])
dbm = 10*numpy.log10(data) + 30
print("dbm values:" + str(dbm))

max = numpy.max(dbm)
print("max power is " + str(max) + " at " + str(freq_array[numpy.where(dbm == max)]/1e6) + " MHz")




