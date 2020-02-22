#!/usr/bin/python3

# Crontab:
# 0 * * * * sudo python3 /home/system/scripts/thingspeak.py
# @reboot sudo python3 /home/system/scripts/thingspeak.py

import socket
import json
from time import strftime,localtime,sleep
import requests
import os, sys
import logging

key = "SYU4LXQT3RHKOD3A"

#Create and configure logger
logging.basicConfig(filename="/var/log/thingspeak_stats.log", format='%(asctime)s %(message)s', filemode='a')
logger=logging.getLogger()
logger.setLevel(logging.DEBUG)

# Check Internet connectivity
def is_connected():
  try:
    host = socket.gethostbyname("www.google.com")
    s = socket.create_connection((host, 80), 2)
    return True
  except:
    return False

# Def the path
path="/data/.folder/"

file_list = []
data_list = []
drive_list= []
other_list= []

# Make list of files in various dir
for root,dirc,fname in os.walk(path):
    for f in fname:
        file_name = os.path.join(root, f)
        file_list.append(file_name)
        if "/data/.folder/DATA" in file_name:
            data_list.append(os.path.join(root, f))
        elif "/data/.folder/Drive" in file_name:
            drive_list.append(file_name)
        else:
            other_list.append(file_name)

# Calculate Counts
count_total = len(file_list)
count_data = len(data_list)
count_others = len(other_list)
count_drive = len(drive_list)
#prob = data + others

# Calculate Sizes
size_total = int(os.popen('du -sh /data/.folder/').read().split()[0].strip('G'))
size_data = int(os.popen('du -sh /data/.folder/DATA').read().split()[0].strip('G'))
size_drive = int(os.popen('du -sh /data/.folder/Drive').read().split()[0].strip('G'))
size_others = size_total - (size_data + size_drive)


# Compare function
def changes():
    # Read existing data
    try:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        file_data = os.path.join(dir_path, "data.ini")
        r = open(file_data,'r')
        data = r.read()
        r.close()
        # Write new data
        data2 = [count_total,count_data,count_others,count_drive,size_total,size_data,size_others,size_drive]
        f = open(file_data,'w')
        f.write(str(data2))
        f.close()
        # Compare
        if data == str(data2):
            return True
        else:
            return False
    except FileNotFoundError:
        logger.info("data.ini file not found error")
        sys.exit()

# Log data to /var/log/thingspeak_stats.log
ctime = strftime("%Y-%m-%d %H:%M:%S +0530", localtime())
logger.info(str(("Data Fetched=",ctime, " total=",count_total, " data=",count_data, " others=",count_others, " drive=",count_drive, "total_size=",size_total, "data_size=",size_data, "others_size=",size_others, "drive_size=",size_drive)))

# Upload Data to Thingspeak
def thing():
    payload = {"write_api_key":key,"updates":[{"created_at":ctime,"field1":count_total,"field2":count_data,"field3":count_others,"field4":count_drive,"field5":size_total,"field6":size_data,"field7":size_others,"field8":size_drive}]}
    url = 'https://api.thingspeak.com/channels/992766/bulk_update.json'
    headers = {'content-type': 'application/json'}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    return response

while True:
    if changes():
        logger.info("Same Data, Skipped uploading data")
        break
    else:
        if is_connected():
            response = thing()
            if response.status_code == 202:
                logger.info(("Data successfully uploaded= ", str(response.status_code)))
                break
            else:
                logger.error(("HTTP Error Code= ", str(response.status_code)))
                sleep(60)
                continue
        else:
            logger.error('Error: Internet Connection down, Retrying after 60 seconds\n')
            sleep(60)
            continue
