import subprocess
import os, sys, shutil
import xml.etree.ElementTree as ET
import asyncio

## SCAN FUNCTIONS ## = runs subprocess tsscan

##ASTRA - 11229000000, 22000000
##EUTEL - 11096000000, 29950000

# satellite - nit-scan, requires accurate starting frequency & symbolrate for lock
# When tuning parameters are specified, tsscan reads the NIT from that transponder. The NIT is then analyzed and all referenced transponders - with all tuning parameters - are found here.
# No NIT in a satellite transponder means no way to scan the network from this transponder. Not all transponders carry the NIT.

def satScan(satName, freq, symb, pol):
    try:
        subprocess.run(["/usr/bin/tsscan", "--verbose", "--nit-scan", "--frequency", freq, "--polarity", pol,
            "--symbol-rate", symb, "--delivery-system", "DVB-S2", "--service-list","--save-channels", "sat_streams/sat_tuning_data/" + satName + '.xml'], check=True)
    except subprocess.CalledProcessError as e:
        print(e)

    
# terrestrial - uses uhf-band frequencies
# The UVH/VHF band scan is typically for terrestrial networks. This is the default. Since the band is limited to typically max 50 different known frequencies,
# the scan operation tests them all. Moreover, knowing the exact tuning parameters is not necessary to a successful tuning.

def terrScan():
    try:
        subprocess.run(["/usr/bin/tsscan", "--verbose", "--uhf-band", "--service-list", "--save-channels", "terr_streams/terr_tuning_data/terr_scan.xml"])       
    except:
        print('ERROR')

## TRANSMISSION TUNING INFO - returns tuning parameters for each frequency from scan results    

# satellite - requires filename of saved XML satellite scans
def satNetworkInfo(satName):
    try:
        xml = ET.parse("sat_streams/sat_tuning_data/" + satName)
        root = xml.getroot()
        network = []
        for dvbs in root.iter('dvbs'):
            network.append(dvbs.attrib)
        for dict in network:
            deliverySystem = 'system'
            if deliverySystem not in dict:
                dict['system'] = 'DVB-S'
        # print(network)
        return network
    except:
        print('error with filename')

# terrestrial
def terrNetworkInfo():
    xml = ET.parse('terr_streams/terr_tuning_data/terr_scan.xml')
    root = xml.getroot()
    network = []
    for dvbs in root.iter('dvbt'):
        network.append(dvbs.attrib)
    # print(network)
    return network

## SERVICE LIST INFO - returns dictionary of services for each frequency

# satellite - requires filename of saved XML satellite scans
def satServicesInfo(satName):
    xml = ET.parse("sat_streams/sat_tuning_data/" + satName)
    root = xml.getroot()

    servicesList = {}

    for ts in root.findall('.//ts'):
        dvbs = ts.find('dvbs')  # Find the <dvbs> node within the <ts> node
        if dvbs is not None:
            frequency = dvbs.get('frequency')  # Access the frequency attribute
            name_list = [service.get('name') for service in ts.findall('.//service')]
            servicesList[frequency] = name_list
    # print(servicesList)
    return servicesList

# terrestrial
def terrServicesInfo():
    xml = ET.parse('terr_streams/terr_tuning_data/terr_scan.xml')
    root = xml.getroot()

    servicesList = {}

    for ts in root.findall('.//ts'):
        dvbt = ts.find('dvbt')  # Find the <dvbs> node within the <ts> node
        if dvbt is not None:
            frequency = dvbt.get('frequency')  # Access the frequency attribute
            name_list = [service.get('name') for service in ts.findall('.//service')]
            servicesList[frequency] = name_list
    # print(servicesList)
    return servicesList

## RECORD FUNCTIONS ## - runs subprocess tsp - uses tuning parameters from tsscan - record time set to 10 seconds - 
## used in conjunction with [transmission]NetworkRecord & [transmission]ChannelRecord to record and analyze streams

# satellite 
def satRecord(network):
    if os.path.exists('sat_streams/errorLog.txt'):
        os.remove('sat_streams/errorLog.txt')
    try:
        subprocess.check_output(["/usr/bin/tsp","--verbose", "-I", "dvb",
            "--signal-timeout", str(8),
            "--delivery-system", str(network['system']),
            "--frequency", str(network['frequency']),
            "--polarity", str(network['polarity']),
            "--symbol-rate", str(network['symbolrate']),
            "--modulation", str(network['modulation']),
            "--fec-inner", str(network['FEC']),
            "-P", "until", "--seconds", str(10),
            "-O", "file", "sat_streams/recordings/" + str(network['frequency']),
            "-P", "analyze", "--wide-display", "--output-file", "sat_streams/service_list/" + "TSinfo - " + str(network['frequency']) + ".conf"])
    except:
        print('ERROR')
        ## removes created empty service list file due to error
        os.remove(r"sat_streams/service_list/" + "TSinfo - " + str(network['frequency']) + ".conf")
        ## saves modulation parameters in error log file
        with open('sat_streams/errorLog.txt', 'a') as f:
            f.write('Error recording frequency ' +
                    str(network['frequency']) + ' ' +
                    str(network['symbolrate']) + ' ' +
                    str(network['polarity']) + ' ' +
                    str(network['system']) + ' ' +
                    str(network['modulation']) + ' ' +
                    str(network['FEC']) + '\n')

# terrestrial 
def terrRecord(network):
    if os.path.exists("terr_streams/errorLog.txt"):
        os.remove('terr_streams/errorLog.txt')
    try:
        subprocess.check_output(["/usr/bin/tsp","--verbose", "-I", "dvb",
            "--signal-timeout", str(8),
            "--delivery-system", 'DVB-T',
            "--frequency", str(network['frequency']),
            "--modulation", str(network['modulation']),
            "-P", "until", "--seconds", str(8),
            "-O", "file", "terr_streams/recordings/" + str(network['frequency']),
            "-P", "analyze", "--wide-display", "--output-file", "terr_streams/service_list/" + "TSinfo - " + str(network['frequency']) + ".conf"])
    except:
        print('ERROR')
        ## removes empty service list file due to error
        os.remove(r"terr_streams/service_list/" + "TSinfo - " + str(network['frequency']) + ".conf")
        ## saves modulation parameters in error log file
        with open('terr_streams/errorLog.txt', 'a') as f:
            f.write('Error recording frequency ' +
                    str(network['frequency']) + ' ' +
                    str(network['modulation']) + '\n')
            

## FREQUENCY RECORD ## records all channels on specified frequency

def satFreqRecord(satName,freq):
    frequencyList = satNetworkInfo(satName)
    # print(frequencyList)
    for frequency in frequencyList:
        if frequency['frequency'] == freq:
            print(frequency)
            satRecord(frequency)
    print('FINISHED RECORDING')


def terrFreqRecord(freq):
    frequencyList = terrNetworkInfo
    # print(frequencyList)
    for frequency in frequencyList:
        if frequency['frequency'] == freq:
            print(frequency)
            terrRecord(frequency)
    print('FINISHED RECORDING')

## NETWORK RECORD FUNCTIONS ## - loops through all frequencies on the network and records all channels

# satellite
def satNetworkRecord(satName):
    frequencyList = satNetworkInfo(satName)
    print(frequencyList)
    for frequency in frequencyList:
        satRecord(frequency)
    print('FINISHED RECORDING')
    
# terrestrial
def terrNetworkRecord():
    frequencyList = terrNetworkInfo()
    print(frequencyList)
    for frequency in frequencyList:
        terrRecord(frequency)
    print('FINISHED RECORDING')

## FOLDER DELETION FUNCTIONS ##

# satellite
def satRecordingsDeleteFolder():
    ## removes previous record folder
    if os.path.exists("sat_streams/recordings"):
        shutil.rmtree("sat_streams/recordings")
        ## creates new recordings folder
        os.mkdir("sat_streams/recordings")

def satService_listDeleteFolder():
    ## removes previous service list folder
    if os.path.exists("sat_streams/service_list"):
        shutil.rmtree("sat_streams/service_list")
        ## creates new service list folder
        os.mkdir("sat_streams/service_list")
     
# terrestrial
def terrRecordingsDeleteFolder():
    ## removes previous record folder
    if os.path.exists("terr_streams/recordings"):
        shutil.rmtree("terr_streams/recordings")
        ## creates new recordings folder
        os.mkdir("terr_streams/recordings")
        
def terrService_listDeleteFolder():
    ## removes previous service list folder
    if os.path.exists("terr_streams/service_list"):
        shutil.rmtree("terr_streams/service_list")
        ## creates new service list folder
        os.mkdir("terr_streams/service_list")




# satServicesInfo('Astra.xml')
# terrServicesInfo()
satNetworkInfo('Astra.xml')
# satNetworkRecord('Astra.xml')



# satFreqRecord('Astra.xml', '12,551,500,000')