#!/usr/bin/env python3
'''
Make a direct MQTT connection to the given IP address and submit a scan request (the payload).  
Author: Randy Herban, Xiangbo Meng @ Notre Dame
'''
import paho.mqtt.client as mqtt
import queue
import argparse
import time
import simplejson as json
import numpy
import base64
import matplotlib as plt
from scipy import signal

payload = {
  'task_name': 'tasks.legacy.rf.scan.periodogram',
  'arguments': 
  {
    "output_topic":"radiohound/clients/data/local",
    "fmin":2000e6,
    "fmax":2020e6,
    "N_periodogram_points":1024,
    "gain":1,
    "batch_id":0, # Can be set to link multiple scans together.  Not implemented in GUI yet.  
  },
}

# The Radiohound hardware does not have separate I and Q outputs.  
# I and Q are recombined in a hardware hybrid to perform image rejection, and then sampled with a single A/D converter.
# Uncomment below for raw ADC output (real samples). 
#
# payload = {
#   'task_name': 'tasks.legacy.rf.scan.raw',
#   'arguments': 
#   {
#     "output_topic":"radiohound/clients/data/local",
#     "center_frequency":2000e6,
#     "gain":1,
#     "batch_id":0,
#   },
# }

timeout = 10
response = queue.Queue() # This holds the messages from the node

parser = argparse.ArgumentParser(description='RadioHound Scan')
parser.add_argument('ip_address', type=str)
args = parser.parse_args()

# Create callback function for MQTT to receive message and add to queue
def on_message(client, userdata, msg):
  global response
  payload = json.loads(msg.payload.decode())
  # If we get a retained message (old data), ignore it
  if msg.retain==1:
    return
  response.put(payload)

client = mqtt.Client()
client.on_message = on_message
client.connect(args.ip_address, 1883, 60)
client.subscribe('radiohound/clients/feedback/#',0)
client.subscribe('radiohound/clients/data/#',0)
client.loop_start()

print(f"Sending command: {payload}")
client.publish("radiohound/clients/command/command_to_all", payload=json.dumps(payload))

start_time = time.time()
# Enter a loop which exits after timeout or we receive data from the node
while True:  
    if time.time() - start_time > timeout:
      print(f"Timed out")
      break
     
    if not response.empty():
      message = response.get()
      # Ignore feedback messages, but this can be used to check for failures
      if 'status' in message:
        continue

      if message['metadata']['data_type'] == 'periodogram':
        # Unpack the data from the json and show some sample data
        data = numpy.frombuffer(base64.b64decode(message['data']), dtype=message['type'])
        print(f"Received {type(data)} with {data.size} elements")
        print(data)
        break


      if message['metadata']['data_type'] == 'raw':
        decoded_data =  numpy.frombuffer(base64.b64decode(message['data']), dtype=message['type'])
        volt_data = (decoded_data.astype(numpy.float32)/127.5)*0.512 - 0.512
        print(decoded_data[0:8])  # raw integer values from adc
        print(volt_data[0:8])     # converted voltage values
        # perform FFT, fixed sample rate of 48msps and arbitrary nperseg
        f, psd = signal.welch(volt_data, fs=48e6, nperseg=1024)
        print(f)
        print(psd[0:8])
        # plot the spectrum, adjusting frequency to to be centered rather than left justified
        # low path below 1GHz uses lower-side band mixing, so flip the spectrum.  high path uses upper-side band mixing
        # plt.plot(f+message['center_frequency']-12e6, 10*numpy.log10(psd[::-1]))
        # plt.xlabel('frequency [Hz]')
        # plt.ylabel('PSD 10*log10(V**2/Hz)')
        # plt.show()
        break

