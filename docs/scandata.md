```javascript
{
   "data": *,                                //See 'Understanding the Data' below
   "type":"float32",
   "mac_address":"98f07b24025a",
   "short_name":"Beagle V3.4-016 ",
   "sample_rate":24000000.0,
   "center_frequency":2000000000.0,
   "timestamp":"2023-05-26T18:24:53.958385+00:00",
   "software_version":"v0.10b25",            //optional
   "latitude":41.69955333118339,             //optional
   "longitude":-86.23723130815955,           //optional
   "altitude":0.0,                           //optional
   "batch":0,                                //optional - corresponds with batch_id from request
   "hardware_version":"3.4",                 //optional - RadioHound specific
   "hardware_board_id":"016",                //optional - RadioHound specific
   "gain":1,                                 //optional
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
