#!/usr/bin/python3

# Crontab:
# 0 * * * * sudo python3 /home/system/scripts/thingspeak.py
# @reboot sudo python3 /home/system/scripts/thingspeak.py


import socket
import json
from time import strftime,localtime,sleep
import requests
import os
import logging

key = "SYU4LXQRY6BKOD3A"

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

path="/data/.folder/"

file_list = []
data_list = []
drive_list= []
other_list= []

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


total = len(file_list)
data = len(data_list)
others = len(other_list)
drive = len(drive_list)

def thing():
    ctime = strftime("%Y-%m-%d %H:%M:%S +0530", localtime())
    logger.info(str(("Data Fetched=",ctime, " total=",total, " data=",data, " others=",others, " drive=",drive)))
    # Upload Temperature Data to thingspeak.com
    payload = {"write_api_key":key,"updates":[{"created_at":ctime,"field1":total,"field2":data,"field3":others,"field4":drive}]}
    url = 'https://api.thingspeak.com/channels/992766/bulk_update.json'
    headers = {'content-type': 'application/json'}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    return response

while True:
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
