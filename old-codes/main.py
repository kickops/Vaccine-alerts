#!/usr/bin/env python
#Author: Kicky

import datetime
import json
import os
import pytz
import random
import requests
import time
from twilio.rest import Client

tz_india = pytz.timezone('Asia/Kolkata')
#pin_codes = ["096","006","081","035","030","028","010","004","102"]


with open ('headers.json') as f:
    headers_list = json.load(f)

def get_slots_by_pincode(pincode="600096"):
  try:
    URL = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode=%s&date=%s'%(pincode,datetime.datetime.now(tz_india).strftime("%d-%m-%Y"))
    headers = random.choice(headers_list)
    r = requests.Session()
    r.headers = headers
    resp = r.get(URL)
    if not resp.status_code == 200: 
       return [] 
    all_sessions = [(center['name'], session['date'], session['vaccine'], session['available_capacity']) for center in resp.json()['centers'] for session in center['sessions'] if session['min_age_limit']==18]
    return all_sessions
  except Exception as error:
    print("Unable to establish connection")


def send_whatsapp(msg):
   account_sid = os.environ['TWILIO_ACCOUNT_SID']
   auth_token = os.environ['TWILIO_AUTH_TOKEN']
   client = Client(account_sid, auth_token)
   
   message = client.messages.create(
                                 body=msg,
                                 from_='whatsapp:+14155238886',
                                 to='whatsapp:+919003111105'
                             )
   print(message.sid)


def main():
    all_shots = []
    available_list=[]
    complete_list = []
    for pin in range(130):
       code = "600{}".format(pin)
       all_slots = get_slots_by_pincode(pincode=code)
       if all_shots:
          for centre in all_shots:
          ## Filter only covaxin and if slots are available 
              if centre[2] == "COVAXIN" and centre[3] > 0:
                   entry = (centre[0], centre[1], centre[3])
                   line = "Hospital:{}\nDate:{}\nSlots:{}".format(centre[0], centre[1], centre[3])
                   available_list.append(entry)
                   send_whatsapp(line) 
          complete_list.extend(all_slots)
       else:
          break
     
    print(available_list)

## MAIN
interval = 600
while True:
   main()
   time.sleep(interval)
