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

########################################################
TWILIO_ACCOUNT_SID = "XXXXXXXXXXXX"
TWILIO_AUTH_TOKEN = "XXXXXXXXXXXXX"
whatsapp_numbers = ["90XXXXXXXX"]
#########################################################
min_age=18
tz_india = pytz.timezone('Asia/Kolkata')
interval=600
pincodes = [4,6,10,18,30,35,36,66,81,96,102,116]
preferred_vaccine = ["COVAXIN"]
filename="vaccines-list.txt"
weeks_to_check = 2
outfile = "available-slots.txt"

account_sid = TWILIO_ACCOUNT_SID 
auth_token = TWILIO_AUTH_TOKEN
client = Client(account_sid, auth_token)

today_obj=datetime.datetime.now(tz_india)
today=today_obj.strftime("%d-%m-%Y")

calender_weeks = [today]
for i in range(1,weeks_to_check):
   new_date = today_obj + datetime.timedelta(days=7 * i)
   calender_weeks.append(new_date.strftime("%d-%m-%Y"))



with open ('headers.json') as f:
    headers_list = json.load(f)


def send_whatsapp(msg):
   print("came in")
   for number in whatsapp_numbers:
      time.sleep(1)
      dest_number="whatsapp:+91{}".format(number)
      print dest_number
      message = client.messages.create(
                                 body=msg,
                                 from_='whatsapp:+14155238886',
                                 to=dest_number
                             )
      print(message.sid)


def make_calls():
   for number in whatsapp_numbers:
      dest_number="+91{}".format(number)
      call = client.calls.create(
                     twiml='<Response><Say>Hey there!, I found new vaccine slots for you</Say></Response>',
                     to=dest_number,
                     from_='+19046028524'
                 )
      print(call.sid)


def send_sms(msg):
   for number in whatsapp_numbers:
      dest_number="+91{}".format(number)
      message = client.messages.create(
                           body=msg,
                           from_='+19046028524',
                           to=dest_number
                       )
      print(message.sid)


def get_slots_by_pincode(pincode, date):
    try:
        URL = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode=%s&date=%s'%(pincode,date)
        headers = random.choice(headers_list)
        r = requests.Session()
        r.headers = headers
        resp = r.get(URL)
        if not resp.status_code == 200: 
           return [] 
        all_sessions = [(center['name'], session['date'], session['vaccine'], session['available_capacity_dose1']) for center in resp.json()['centers'] for session in center['sessions'] if session['min_age_limit']==min_age]
        return all_sessions

    except Exception as error:
        print("Unable to establish connection")
        return "Error"


def process_stuff(code, date):
    all_slots = []
    time.sleep(random.randint(1,30))
    all_slots = get_slots_by_pincode(code, date)
    if all_slots:
       print(all_slots)
       for centre in all_slots:
       ## Filter only covaxin and if slots are available
           if centre[2] in preferred_vaccine and centre[3] > 2:
                line = "Hospital:{}\nDate:{}\nSlots:{}\nVaccine:{}\nPostedTime:{}".format(centre[0], centre[1], centre[3], centre[2],today_obj.strftime("%d-%m-%Y-%H-%M"))
                entry = "{}|{}|{}|{}|{}".format(today_obj.strftime("%d-%m-%Y-%H-%M"),centre[0], centre[1], centre[3], centre[2])
                print("==========================VACCINES FOUND======================================")
                print(line)
                print("===============================================================================")
                notifier.notify(line)
                with open(outfile, "a") as out:
                   out.write(entry + "\n")
                make_calls()
                send_whatsapp(line)
                send_sms(line)


def get_slots(date):
    processes = []
    for pin in pincodes:
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
   time.sleep(3)

