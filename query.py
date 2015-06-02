#!/usr/bin/env python
#
# Example of querying workitems
#
import json
import urllib
import jazz
from oslc.cm.services import services

# Load a json credentials file
json_data=open('creds.json')
data = json.load(json_data)
json_data.close()

# key into the rtc dict object in credentials file
project_key = 'original'

# pulled from credential file
project = data["rtc"][project_key]
project_name = project['project_name']
base_url = project['url'];
rtc_user = project['user'];
rtc_pass = project['password'];

# Grab a connection to the WarRoom
conn = jazz.connection( base_url, rtc_user, rtc_pass )
cur_services = services( conn )

# OSLC querying
# https://jazz.net/wiki/bin/view/Main/ResourceOrientedWorkItemAPIv2#Querying_Work_Items
query_url = cur_services.get_project_area( project_name )['workitem_url']

query_terms ='oslc_cm.query=' + urllib.quote( 'rtc_cm:state!="{closed}" and dc:modified<"{-37M}"  ' )
query_properties = '&oslc_cm.properties=' + urllib.quote( 'dc:title,dc:identifier,rtc_cm:state,dc:modified' )
query_pagination = '&oslc_cm.pageSize=3'
query_other = '&_pretty=true'

query_uri = ".json?%s%s%s%s" % ( query_terms, query_properties, query_pagination, query_other)

print "query_uri: [ %s ]" % (query_uri )

query_url = cur_services.get_project_area( project_name )['workitem_url'] + query_uri
running_query = True

# Paging through results
while running_query:
    req = conn.get( query_url, headers={'accept': 'application/json', 'content-type':'application/json'} )

    if req.status_code == 200:
        print req.text
        page = json.loads( req.text )
    else:
        running_query = False

    if 'oslc_cm:next' in page:
        query_url = page[ 'oslc_cm:next' ]
    else:
        running_query = False

    print page

    #running_query = False
