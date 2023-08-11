import subprocess
from datetime import datetime
import os, sys, shutil
import time


countries=["FR","ES","DE","GB"]
## Asks user to pick satellite or terrestrial scan
user_scan_input = ""
while True:
    user_scan_input = input("Pick scan type: 1) Satellite | 2) Terrestrial \n")
    
    if user_scan_input == "1":
        scan_type = "satellite"
        while True:
            sat_choice = str(input("Which satellite are you using? \nPlease use uppercase character constant with E (east) or W (west) as separator e.g - S19E2, S13E0, S0W8"))
            break
        break
    elif user_scan_input == "2":
        scan_type = "terrestrial"
        while True:
            country_choice = str(input("Which Country are you using? \n FR - France \n ES - Spain \n DE - Germany \n GB - United Kingdom \n")).upper()
            print(country_choice)
            if country_choice not in countries:
                print("Please type FR, ES, DE or GB")
                continue
            else:
                break
        break
    else:
        
        continue
           
        
# SATELLITE SCAN
if scan_type == "satellite":
    ## runs TSDuck process - tsscan - nit-scan for satellite
    date = datetime.now().strftime("_%Y_%m_%d")
    f = open(sat_choice + date + ".txt", "w")
    process = subprocess.run(["/usr/bin/w_scan", "-fs", "--satellite", sat_choice], stdout=f)
# TERRESTRIAL SCAN
elif scan_type == "terrestrial":
    ## runs TSDuck process - tsscan - uhf-band for terrestrial
    date = datetime.now().strftime("_%Y_%m_%d")
    f = open(country_choice + date + ".txt", "w")
    subprocess.run(["/usr/bin/w_scan", "-ft", "--country", country_choice], stdout=f)




## Script stopwatch with scan function call
# if record == True:
#     start = time.time()
#     scan()
#     end = time.time()
#     print(f" record time taken to run was {end-start} seconds \n")
# else:
#     print('\033[1m' + "Please find json or XML in project folder after successful frequency scan \n")
# 
