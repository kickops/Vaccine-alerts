#!/usr/bin/env python
#Author: Kicky

import datetime
import json
import multiprocessing
import notifier
import os
import pytz
import random
import requests
import time
from twilio.rest import Client

min_age=18
tz_india = pytz.timezone('Asia/Kolkata')
interval=600
preferred_vaccine = ["COVAXIN", "COVISHIELD"]
filename="vaccines-list.txt"
whatsapp_numbers = ["9003111105", "9841821061"]
weeks_to_check = 3

today_obj=datetime.datetime.now(tz_india)
today=today_obj.strftime("%d-%m-%Y")

calender_weeks = [today]
for i in range(1,weeks_to_check):
   new_date = today_obj + datetime.timedelta(days=7 * i)
   calender_weeks.append(new_date.strftime("%d-%m-%Y"))



with open ('headers.json') as f:
    headers_list = json.load(f)


def send_whatsapp(msg):
   account_sid = os.environ['TWILIO_ACCOUNT_SID']
   auth_token = os.environ['TWILIO_AUTH_TOKEN']
   client = Client(account_sid, auth_token)
   for number in whatsapp_numbers:
      time.sleep(1)
      message = client.messages.create(body=msg,from_='whatsapp:+14155238886',to='whatsapp:+91{}'.format(number))


def get_slots_by_pincode(pincode, date):
    try:
        URL = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode=%s&date=%s'%(pincode,date)
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


def process_stuff(code, date):
    all_slots = []
    time.sleep(random.randint(1,40))
    all_slots = get_slots_by_pincode(code, date)
    if all_slots:
       print(all_slots)
       for centre in all_slots:
       ## Filter only covaxin and if slots are available
           if centre[2] in preferred_vaccine and centre[3] > 0:
                entry = (centre[0], centre[1], centre[3])
                line = "Hospital:{}\nDate:{}\nSlots:{}".format(centre[0], centre[1], centre[3])
                with open(filename, 'a') as outfile:
                  outfile.write(line + "\n")
                send_whatsapp(line)
                notifier.notify(line)
                print(line)


def get_slots(date):
    processes = []
    for pin in range(1,130):
       digits = "{0:03}".format(pin)
       code = "600{}".format(digits)
       p = multiprocessing.Process(target=process_stuff, args=(code,date)) 
       processes.append(p)
       p.start()

    for process in processes:
        process.join()


## MAIN
open(filename, 'w').close()
for date in calender_weeks:
   get_slots(date)

