#!/usr/bin/env python
#Author: Kicky

import datetime
import json
import multiprocessing
import os
import pytz
import random
import requests
import time
from twilio.rest import Client

min_age=18
tz_india = pytz.timezone('Asia/Kolkata')
interval=600
vaccine_company = ["COVAXIN", "COVISHIELD"]
filename="vaccines-list.txt"

with open ('headers.json') as f:
    headers_list = json.load(f)


def send_whatsapp(msg):
   account_sid = os.environ['TWILIO_ACCOUNT_SID']
   auth_token = os.environ['TWILIO_AUTH_TOKEN']
   client = Client(account_sid, auth_token)
   message = client.messages.create(body=msg,from_='whatsapp:+14155238886',to='whatsapp:+919003111105')


def get_slots_by_pincode(pincode="600096"):
  try:
    URL = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode=%s&date=%s'%(pincode,datetime.datetime.now(tz_india).strftime("%d-%m-%Y"))
    headers = random.choice(headers_list)
    r = requests.Session()
    r.headers = headers
    resp = r.get(URL)
    if not resp.status_code == 200: 
       return [] 
    all_sessions = [(center['name'], session['date'], session['vaccine'], session['available_capacity']) for center in resp.json()['centers'] for session in center['sessions'] if session['min_age_limit']==min_age]
    return all_sessions

  except Exception as error:
    print("Unable to establish connection")
    return "Error"


def process_stuff(code):
    all_slots = []
    time.sleep(random.randint(1,40))
    all_slots = get_slots_by_pincode(pincode=code)
    if all_slots:
       print(all_slots)
       for centre in all_slots:
       ## Filter only covaxin and if slots are available
           if centre[2] in vaccine_company and centre[3] > 0:
                entry = (centre[0], centre[1], centre[3])
                line = "Hospital:{}\nDate:{}\nSlots:{}".format(centre[0], centre[1], centre[3])
                with open(filename, 'a') as outfile:
                  outfile.write(line + "\n")
                send_whatsapp(line)
                print(line)


def get_slots():
    processes = []
    for pin in range(1,130):
       digits = "{0:03}".format(pin)
       code = "600{}".format(digits)
       p = multiprocessing.Process(target=process_stuff, args=(code,)) 
       processes.append(p)
       p.start()

    for process in processes:
        process.join()


## MAIN
open(filename, 'w').close()
while True:
   get_slots()
   print("============================================================================================")
   time.sleep(interval)
