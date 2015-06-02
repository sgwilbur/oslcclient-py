#!/usr/bin/env python

import requests
import jazz
import cloudant
import json
import pprint
import urllib
from string import Template

# Load vcap servicefile
json_data=open('creds.json')
data = json.load(json_data)
json_data.close()

project_key = 'original'
project = data["rtc"][project_key]

base_url = project['url'];
rtc_user = project['user'];
rtc_pass = project['password'];

# Grab a connection to the WarRoom
conn = jazz.connection( base_url, rtc_user, rtc_pass )
sess = conn.get_session()

wi_url = base_url + '/oslc/workitems/15028.json?oslc_cm.properties=dc:identifier,dc:title,dc:subject'
#wi_url = base_url + '/oslc/workitems/18351.json'

req = sess.get( wi_url )


print req.text
