# Connecting to MQTT
Use an MQTT client and connect to radiohound.ee.nd.edu port 1883 (we run the mosquitto MQTT server).
Send a JSON-formatted announce packet to the topic radiohound/clients/announce/MAC_ADDRESS containing the following:

```javascript
{
   "message":"INITIAL",
   "payload":{
      "mac_address":"98f07b24025a",           //unique identifier for the node, used heavily within the platform
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
