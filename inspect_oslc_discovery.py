#!/usr/bin/env python
#
# Example of inspecting the oslc discovery process
#

import json

import jazz
from oslc.cm.services import services

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

# OSLC querying
# https://jazz.net/wiki/bin/view/Main/ResourceOrientedWorkItemAPIv2#Querying_Work_Items
cur_services = services( conn )

pas = cur_services.get_project_areas()

for key, value in pas.iteritems():
    print " %s => %s " % ( key, value )
