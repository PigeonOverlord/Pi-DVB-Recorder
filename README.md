# Pi Stream Recorder

Scans Terrestrial and Satellite streams

## Prerequisites

Requires [TSduck](https://tsduck.io) installation

Satellite/Terrestrial Tuner with up to date drivers

## Usage
```
1. Connect PI unit to satellite/terrestrial tuner with cable feed
2. Run pMenu.py script
3. Select Terrestrial or Satellite scan on display
4. Select 'Record: Yes' to run scan & then record
5. Select 'Record: No' to only do scan
6. Select 'Back' to go back one menu
```
+ If scan is successful, results are written to scan.xml and x2j.json
+ recordings can be found in sat_streams/recordings or terr_streams/recordings
+ no current user feedback on PI display for errors, please check console for errors
+ terrestrial scan requires no input as it uses standard uhf-bands
+ satellite scan requires valid frequency, symbol rate & polarity for the scan to initially lock. The satellite scan is initially set up for Astra 19.2 but can be re-calibrated with the correct satellite parameters

#### Useful TSduck console commands

+ tslsdvb - list connected tuner devices' driver and DVB compatibility
+ tsp - records channels on frequency ```e.g tsp -I dvb -a 0 --delivery-system DVB-S2 --frequency 10744000000 --polarity horizontal -s 22000000  -O file sat_test.ts```
+ tsscan - scans transponder network | use --nit-scan for DVB-S2 & --uhf-band for DVB-T ```e.g tsscan --uhf-band --service-list```

#### Console script - pScanner
Initial console script for building of functions - was expanded to utilise pi display, now obsolete
```
1. run pScanner.py to run console script 
2. follow user input (1-2) to scan or record
```
### Useful libraries for scanning and troubleshooting

+ w_scan_cpp - uses satellite and region parameters to scan frequencies ```e.g w_scan_cpp -fs -s S19E2 -c DE```
+ dvbv5_scan - requires initial scan file and the LNB to be specified ```e.g dvbv5_scan Astra-1N-19.2E --lnbf=EXTENDED --output=FILENAME```


