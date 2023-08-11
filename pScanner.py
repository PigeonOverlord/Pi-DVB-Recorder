import subprocess
import json
from datetime import datetime
import os, sys, shutil
import time
import csv


## Asks user to pick satellite or terrestrial scan
user_scan_input = ""
while True:
    user_scan_input = input("Pick scan type: 1) Satellite | 2) Terrestrial \n")
    
    if user_scan_input == "1":
        scan_type = "satellite"
        break
    elif user_scan_input == "2":
        scan_type = "terrestrial"
        break
    else:
        print("type a number 1-2")
        continue
    
## Asks user if they want to record channels after frequency scan
user_record_input = ""
while True:
    user_record_input = input("Do you want to record after scan?: 1) Yes | 2) No \n")
    
    if user_record_input == "1":
        record = True
        break
    elif user_record_input == "2":
        record = False
        break
    else:
        print("type a number 1-2")
        continue

        
# SATELLITE SCAN
if scan_type == "satellite":
    ## runs TSDuck process - tsscan - nit-scan for satellite
    subprocess.run(["/usr/bin/tsscan", "--verbose", "--nit-scan", "--frequency", "11347000000",
                          "--symbol-rate", "22000000", "--delivery-system",
                         "DVB-S2", "--save-channels", "scan.xml"])
# TERRESTRIAL SCAN
elif scan_type == "terrestrial":
    ## runs TSDuck process - tsscan - uhf-band for terrestrial
    date = datetime.now().strftime("_%Y-%m-%d_%H-%M-%S")
#     f = open('/home/obs/stream_recorder/terr_streams/service_list' + date + ".txt", "w")
    subprocess.run(["/usr/bin/tsscan", "--verbose", "--uhf-band", "--save-channels", "scan.xml"])

    
## converts scan from XML to json 
subprocess.run(["/usr/bin/tsxml", "--json", "scan.xml", "--channel", "--output", "x2j.json"])

##  Scan function
def scan():
    
    ## Empty list for network data
    network = []
    ## Sets meta_data as previously scanned json file
    meta_data = json.load(open("x2j.json","r"))
    ## Counter for looping through meta_data nodes
    meta_counter = 0

    for node in meta_data[meta_counter]['#nodes']:
        ## empty dictionary for scanned results
        ch_info = {}
        ## empty list to store channel names
        ch_names = []
        for subnode in node['#nodes']:
            try:
                ## SATELLITE - if subnode #name is dvbs
                if subnode['#name'] == 'dvbs':
                    ## adds frequency, symbolrate, polarity and modulation to empty ch_info dictionary
                    ch_info.update({'ch_frequency':subnode['frequency'], 'ch_symbolrate':subnode['symbolrate'],
                    'ch_polarity':subnode['polarity'], 'ch_modulation':subnode['modulation']})
                ## if subnode #name is service
                if subnode['#name'] == 'service':
                    ## appends channel name to ch_names list
                    ch_names.append(subnode['name'])
                ## TERRESTRIAL - if subnode #name is dvbt
                if subnode['#name'] == 'dvbt':
                    ## adds frequency, bandwidth and modulation to empty ch_info dictionary
                    ch_info.update({'ch_frequency':subnode['frequency'], 'ch_bandwidth':subnode['bandwidth'], 'ch_modulation':subnode['modulation']})
            ## if subnode does not contain channel info or name, increase loops counter to next array position and restarts loop     
            except:
                meta_counter += 1
        ## appends ch_names list to ch_info dictionary 
        ch_info.update({'ch_list':ch_names})
        ## appends all ch_info to network list
        network.append(ch_info)

    print(network)
    
    
    ## Satellite record function
    def sat_record(ch_frequency, ch_polarity, ch_symbolrate, ch_modulation, ch_list):
        frequency = ch_frequency
        polarity = ch_polarity
        symbolrate = ch_symbolrate
        modulation = ch_modulation
        ## unused variables - but needed to be passed to function
        channels = ch_list
        ## runs TSDuck record function - takes in frequency, polarity, symbolrate and modulation
        return subprocess.run(["/usr/bin/tsp","--verbose", "-I", "dvb", "--signal-timeout", str(5), "--delivery-system",
            "DVB-S2", "--frequency", str(frequency), "--polarity", str(polarity), "--symbol-rate", str(symbolrate),
            "--modulation", modulation, "-P", "until", "--seconds", str(8), "-O", "file", "sat_streams/recordings/" + str(frequency) + ".ts" ])
        
    ## Terrestrial record function
    def terr_record(ch_frequency, ch_bandwidth, ch_modulation, ch_list):
        frequency = ch_frequency
        modulation = ch_modulation
        ## unused variables - but needed to be passed to function
        bandwidth = ch_bandwidth
        channels = ch_list
        ## runs TSDuck record function - takes in frequency and modulation
        return subprocess.run(["/usr/bin/tsp","--verbose", "-I", "dvb", "--signal-timeout", str(5), "--delivery-system",
            "DVB-T2", "--frequency", str(frequency), "--modulation", modulation, "-P", "until", "--seconds",
            str(8), "-O", "file", "terr_streams/recordings/" + str(frequency) + ".ts" ])
    

    ## Satellite folder creation & record function
    if scan_type == 'satellite':
        ## removes previous record folder
        if os.path.exists("sat_streams/recordings"):
            shutil.rmtree("sat_streams/recordings")
        ## creates new terr_streams folder
        os.mkdir("sat_streams/recordings")
    
        ## for each dictionary in network list - runs satellite record function
        for dict in network:
            sat_record(**dict)
    
    ## Terrestrial folder creation & record function
    elif scan_type == "terrestrial":
        ## removes previous record folder
        if os.path.exists("terr_streams/recordings"):
            shutil.rmtree("terr_streams/recordings")
        ## creates new terr_streams folder
        os.mkdir("terr_streams/recordings")
    
        ## for each dictionary in network list - runs terrestrial record function
        for dict in network:
            terr_record(**dict)
            
## Script stopwatch with scan function call
if record == True:
    start = time.time()
    scan()
    end = time.time()
    print(f" record time taken to run was {end-start} seconds \n")
else:
    print('\033[1m' + "Please find json or XML in project folder after successful frequency scan \n")

