# Connecting to the RadioHound Platform 
- A RadioHound node must be able to uniquely identify itself (using the ethernet mac address) and connect to the RadioHound infrastructure.  Ideally, the RadioHound node should also be able to denote its hardware configuration and / or environment (location, motion, etc.).  
- The RadioHound data infrastructure must be able to provide configuration information for each RadioHound node ("marching orders").
- If a persistent network connection exists, the RadioHound infrastructure should be able to monitor the status of a RadioHound node in the field.     
- RadioHound nodes should utilize the configuration information to control how data is gathered and then periodically report said data to the centralized infrastructure including performance data with respect to processing.  

## Connecting to MQTT
Use an MQTT client and connect to radiohound.ee.nd.edu port 1883 (we run mosquitto).  
Send a JSON-formatted announce packet to the topic `radiohound/clients/announce/MAC_ADDRESS` containing the following:

```javascript
{
   "message":"INITIAL",
   "payload":{
      "mac_address":"98f07b24025a",           //unique identifier for the node, used heavily in the system
      "latitude":41.69955333118339,
      "longitude":-86.23723130815955,
      "altitude":0.0,
      "IP_addr":"10.1.1.1",
      "display_name":"Beagle V3.4-016",       //automatically created from group name and RadioHound version/serial
      "hostname":"025a",                      //last 4 characters of mac address
      "system_version":"Debian GNU/Linux 9 (stretch)",
      "kernelVersion":"4.9.36-ti-r46",
      "groups":[ "Beagle"],                   //sent from server
      "config_version":1684434463,            //if using config sent from server
      "short_name":"",                        //optional nickname, e.g. “Randy’s Office”
      "disk_free":"26G",                      //optional
      "disk_used":"2.6G",                     //optional
      "gitBranch":"HEAD detached at v0.10b25",//optional
      "jobs":{ },                             //optional list of background jobs from experiments
      "ansible_timestamp":1680106088,         //RadioHound specific
      "rh_hardware_version":"3.4",            //RadioHound specific
      "rh_hardware_attached":true,            //RadioHound specific
      "rh_software_version":"v0.10b25",       //RadioHound specific
      "mspVersion":"53",                      //RadioHound specific
   }
}
```


To minimize traffic, we use three levels of announce messages:
- `INITIAL`, sent only at boot: contains full configuration of the node
- `HEARTBEAT`, sent every 10 seconds: GPS, IP address, config version, display name
- `ANNOUNCE`, sent every 60 seconds: Hostname, short_name, disk free/used, ansible timestamp, plus HEARTBEAT items above

Nodes will be marked offline after 20 seconds.

## Receiving commands
Commands to a node will be sent as JSON-formatted packets to two possible topics:

```
radiohound/clients/command/MAC_ADDRESS   ← Update appropriately
radiohound/clients/command/command_to_all
```

The command will have the format and additional arguments can be passed in depending on the task (see below for additional tasks).

```javascript
{
   "task_name":"tasks.name",
   "arguments":{
      "output_topic":"radiohound/clients/data/MAC_ADDRESS/BROWSER_GUID",	//Destination topic in MQTT for reply
   },
},
```

Incoming commands can be queued up and processed as resources are available.  Scan requests from the website are sent in rapid succession to obtain as close to real-time scans as possible.  A command clearing the queue is sent on occassion (more details below).

Commands will have a unique client id (called `browser_guid`) as part of the JSON request or embedded in the `output_topic`.  It is only relevant to ensure a particular response makes its way to the originating client.  

## Sending Feedback
Responses to each command should be sent to the appropriate output_topic specified. Commands with no output should send an acknowledgement packet to this topic with a PASS/FAIL response:
`radiohound/clients/feedback/MAC_ADDRESS`

```javascript
{
   "task":"tasks.legacy.rf.scan.periodogram",
   "status":"PASS",
   "message":null
}
```
```javascript
{
   "task":"tasks.legacy.rf.scan.periodogram",
   "status":"FAIL",
   "message":"frequency out of range"
}
```


# Periodogram Scan Request
The main function of the RadioHound platform is performing a periodogram and this is accomplished with the `tasks.legacy.rf.scan.periodogram` request:

```javascript
{
   "task_name":"tasks.name",
   "arguments":{
      "output_topic":"radiohound/clients/data/MAC_ADDRESS/BROWSER_GUID",	//Destination topic in MQTT for reply      
      "fmin":1990000000,                     //Hertz
      "fmax":2010000000,                     //Hertz
      "N_periodogram_points":1024,           //Number of FFT bins
      "gain":1,                              //IF Gain
      "timeout":10,                          //ignore request after X seconds

      "rbw":23437.5,                         //optional
      "batch_id":0,                          //optional - group scans together, not implemented in GUI
      "additional_info":{                    //optional
         "archiveResult":true                //optional - should result be saved in database
      },
   }
}
```

A periodogram reply will have the following response:
```javascript
{
   "data": *,                                //See 'Understanding the Data' below
   "type":"float32",
   "mac_address":"98f07b24025a",
   "short_name":"Beagle V3.4-016 ",
   "sample_rate":24000000.0,
   "center_frequency":2000000000.0,
   "timestamp":"2023-05-26T18:24:53.958385+00:00",
   "gain":1,
   "software_version":"v0.10b25",
   "latitude":41.69955333118339,             //optional
   "longitude":-86.23723130815955,           //optional
   "altitude":0.0,                           //optional
   "batch":0,                                //optional - corresponds with batch_id from request
   "hardware_version":"3.4",                 //optional - RadioHound specific
   "hardware_board_id":"016",                //optional - RadioHound specific
   "metadata":{
      "data_type":"periodogram",
      "fmin":1988000000.0,                   //Return actual scan boundaries based on hardware capabilities
      "fmax":2012000000.0,
      "n_periodogram_points":1024.0,         //Number of fft bins
      "gps_lock":false,
      "scan_time":0.12714433670043945,       //Time taken to take scan, including pre- and post-processing steps
      "archiveResult":true                   //Should result be saved in database
   },
   "requested":{                             //Originating request
      "fmin":1990000000,
      "fmax":2010000000,
      "span":20000000,
      "rbw":23437.5,
      "samples":1024
   }
}
```



### Understanding the Data 

Scan data is a discrete estimate of the power spectrum over the given span with bins of width RBW.  

The data is stored in a Float32/Single array (adhering to the IEEE754 Standard). The length of the array is N_periodogram_points and the float values are stored in a little endian byte order. When creating the JSON payload for transmission, the data field should encoded using the Base64 alphabet defined in RFC 4648.

------------------------

# Additional Commands

## tasks.admin.reboot
Reboot the node immediately.

## tasks.admin.request_status
Request the current status of the node, returning a heartbeat packet to `radiohound/clients/announce/MAC_ADDRESS`.

## tasks.admin.clear_queue
Commands will have a unique ID to ensure the response will make its way to the originating client.  Commands can be queued up during a scan session and a `clear_queue` command is sent to inform the node that any pending tasks from this client can be safely removed.   
**Expected arguments:**
```javascript
{"arguments": {"browser_guid":"46ec5f20-403e-42d1-a189-489951dd5370"}}
```

