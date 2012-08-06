'''
Created on May 9, 2011

@author: swilbur@gmail.com
'''
import urllib
import httplib2
import re
import pprint
from lxml import etree
#from xml.dom.minidom import parse, parseString
from exceptions import Exception
from jazz import workitem, projectarea

class OslcClient(object):
    # hard-coded for Form Auth
    # todo: add support for Basic Auth
    def __init__(self, server_url, user, password):
        self.__DEBUG_LEVEL__ = 1
        self.base_url = server_url
        self.auth_uri =  '/authenticated/identity'
        
        httplib2.debuglevel=0
        self.http = httplib2.Http( disable_ssl_certificate_validation=True )
        self.http.follow_all_redircts = True
        self.http.follow_redirects = True
#        self.headers = {'content-type': 'text/xml', 'accept': 'application/x-oslc-cm-change-request+xml'}
        self.headers = {'content-type': 'text/xml', 'accept': 'application/rdf+xml'}
        
# TODO: identify namespace mappings to spec/product versions       
        self.oslc_namespaces = {
                                'atom'       : 'http://www.w3.org/2005/Atom',
                                'calm'       : 'http://jazz.net/xmlns/prod/jazz/calm/1.0/',
#                                'dc'   : 'http://purl.org/dc/terms/',
                                'dc'         : 'http://purl.org/dc/elements/1.1/',
                                'dcterms'    : 'http://purl.org/dc/terms/',
                                
                                'jd'         : 'http://jazz.net/xmlns/prod/jazz/discovery/1.0/',
                                'jdb'        : 'http://jazz.net/xmlns/prod/jazz/dashboard/1.0/',
                                'jfs'        : 'http://jazz.net/xmlns/prod/jazz/jfs/1.0/',
                                'jp06'       : 'http://jazz.net/xmlns/prod/jazz/process/0.6/',
                                'jp'         : 'http://jazz.net/xmlns/prod/jazz/process/1.0/',
                                'jpres'      : 'http://jazz.net/xmlns/prod/jazz/presentation/1.0/',
                                'jproc'      : 'http://jazz.net/xmlns/prod/jazz/process/1.0/',
                                'jtp'        : 'http://jazz.net/xmlns/prod/jazz/jtp/0.6/',
                                'ju'         : 'http://jazz.net/ns/ui#',
                                
                                'ns1'        : 'http://jazz.net/xmlns/prod/jazz/process/1.0/',
                                'ns2'        : 'http://schema.ibm.com/vega/2008/',
                                'ns3'        : 'http://purl.org/dc/elements/1.1/',
                                'ns5'        : 'http://open-services.net/ns/qm#',
                                'ns6'        : 'http://open-services.net/xmlns/qm/1.0/',
                                'ns8'        : 'http://jazz.net/ns/qm/rqm#',
                                'ns12'       : 'http:/www.w3.org/2001/XMLSchema-instance',
                                
                                'opensearch' : 'http://a9.com/-/spec/opensearch/1.1/',
                                'oslc'       : 'http://open-services.net/ns/core#',
                                'oslc_cm'    : 'http://open-services.net/xmlns/cm/1.0/',
                                
                                'oslc_qm'    : 'http://open-services.net/xmlns/qm/1.0/',
#                                'oslc_qm'    : 'http://open-services.net/ns/qm#',
                                'oslc_rm'    : 'http://open-services.net/xmlns/rm/1.0/',
                                'oslc_disc'  : 'http://open-services.net/xmlns/discovery/1.0/',
                                
                                'rdf'        : 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
                                'rdfs'       : 'http://www.w3.org/2000/01/rdf-schema#',
                                'rqm'        : 'http://jazz.net/xmlns/prod/jazz/rqm/qm/1.0/',
                                'rqm_qm'     : 'http://jazz.net/ns/qm/rqm#',
                                'rtc_cm'     : 'http://jazz.net/xmlns/prod/jazz/rtc/cm/1.0/',
                                
                                'trs'        : 'http://jazz.net/ns/trs#',
                                }  
     
        # Send initial challenge request for secured resource
        response, content = self.http.request( self.base_url + "/authenticated/identity", 'GET', headers=self.headers)
        
#        print(" >>> initial response: ", response )
#        print(" >>>  initial content: ", content )
        
#        print( "Response to get authenticated/identity:" + response.__str__() )
        if response['x-com-ibm-team-repository-web-auth-msg'] != 'authrequired':
            raise Exception("Server error authenticating: " + response.__str__())

        self.headers['cookie']=  response['set-cookie'] 
        self.headers['content-type'] = 'application/x-www-form-urlencoded'
        
        # TODO: Post login information, Jazz uses j_security_check for FORM auth.
        response, content = self.http.request(self.base_url+'/authenticated/j_security_check' , 'POST',
                            headers=self.headers, body=urllib.urlencode({'j_username': user, 'j_password': password}))

        # Special case, WAS returns the LPTA token here, instead of requiring the first get request to get the JSESSIONID
#        print(" >>> login response: ", response )
#        print(" >>>  login content: ", content )
        if response.__contains__('set-cookie'):
            print( ">>> Found the set-cookie header")
            self.headers['cookie']=  response['set-cookie'] 
        
        
        # Confirm that we are connected, and can grab the secure resource now
#        print( " >>> cookie: ", self.headers['cookie'] )
        response, content = self.http.request( self.base_url + "/authenticated/identity", 'GET', headers=self.headers)
        
#        print(" >>> check response: ", response )
#        print(" >>>  check content: ", content )
        
        if response.__contains__('X-com-ibm-team-repository-web-auth-msg'):
#            print( "Response: " + response.__str__() )
#            print( "Content: " + content.__str__() )
            raise Exception("Login was not successful, server response: " + response.__str__() )
##
## FIXME:  Super hack so this can handle both Tomcat and WAS 
##  It seems that we need to keep the cookie updated for Tomcat but for WAS we want to leave it as
## is. Not sure how this works, so it seems like a hack to me for now.
##
        elif response.__contains__('set-cookie') and "LtpaToken2" not in self.headers['cookie'] :
#            print( ">>> Found the set-cookie header")
#            print( " >>> original  cookie: ", self.headers['cookie'] )
#            print( " >>> new value cookie: ", response['set-cookie'])
            self.headers['cookie']=  response['set-cookie']
            
        self.headers['accept'] = 'application/rdf+xml'
        self.headers['content-type'] = 'text/xml'


    def __login__(self):
        # Grab secured resource to initiate login
        response, content = self.http.request( self.base_url + "/authenticated/identity", 'GET', headers=self.headers)
        
        if response.__contains__('X-com-ibm-team-repository-web-auth-msg'):
        
            if response['x-com-ibm-team-repository-web-auth-msg'] != 'authrequired':
                raise Exception("Server error authenticating: " + response.__str__())
            
            # TODO: Post login information, Jazz uses j_security_check for FORM auth.
            response, content = self.http.request(self.base_url+'/authenticated/j_security_check' , 'POST',
                                headers=self.headers, body=urllib.urlencode({'j_username': self.user, 'j_password': self.password}))
            
            # Confirm that we are connected, and can grab the secure resource now      
            response, content = self.http.request( self.base_url + "/authenticated/identity", 'GET', headers=self.headers)
            
            if response.__contains__('X-com-ibm-team-repository-web-auth-msg'):
                raise Exception("Login was not successful, server response: " + response.__str__() )


#
# Helper method to ease changes in context root
#
    def getContextRoot(self):
# TODO: Included port and context root as instance variables
        return self.base_url

#
#  Generic helper to grab a URLs
#
    def authenticatedRequest( self, type, url, headers, content={} ):
        print( 'unimplemented' )


    def get( self, url ):
        return  self.getH( url, self.headers )

    def getH( self, url, headers ):

        print( " >>> getH headers")
        pprint.pprint( headers )
        response, content = self.http.request(url, 'GET', headers=headers)
        print( " >>> getH response")
        pprint.pprint( response )

        if response.__contains__('X-com-ibm-team-repository-web-auth-msg'):
            raise Exception("Need to authenticate and try again.")
        
        if response.status != 200:
            raise Exception("OslcClient response status != 200 !!!" + response.__str__() + ' content: ' + content.__str__() )
        return content

#
#  POST helpers
#
    def post( self, url , content):
        return self.postH( url, content, self.headers )
    
    def postH( self, url, content, headers ):
        raise Exception("POST unimplemented")

## Inflight testing of these methods
    def postXML(self, url, contentXML ):
        headers = self.headers
#        headers = {'Content-type': 'application/x-oslc-cm-change-request+xml', 'accept': 'text/xml'}

        response, content = self.http.request(url, 'POST', contentXML, headers=headers)

        if response.__contains__('X-com-ibm-team-repository-web-auth-msg'):
            raise Exception("Need to authenticate and try again.")
#        if response.status != 200:
#            raise Exception("OslcClient response status != 200 !!!" + response.__str__())
        return content
    
    def postJSON(self, url, contentJSON ):
        headers = self.headers
        headers['content-type'] = 'application/x-oslc-cm-change-request+json'
        headers['accept'] = 'text/json'
        pprint.pprint( headers )

        response, content = self.http.request(url, 'POST', contentJSON, headers=headers)
        return content

#
#  PUT Helpers
#
    def put( self, url , content):
        return self.postH( url, content, self.headers )
    
    def putH( self, url, content, headers ):
        raise Exception(" PUT unimplemented")

    def debug_print( level, message ):
        if( level > self.__DEBUG_LEVEL__ ):
            print( message )

#
#  Generic xpath helper
#
    def getElembyXpath(self, document_str, xpath ):
        tree = etree.fromstring( document_str )
##        print( etree.tostring(tree, pretty_print=True) )
        elem = tree.xpath( xpath, namespaces=self.oslc_namespaces )
        return elem

#
# Grab the services discovery document
#
    def getRootServicesDoc(self):
        content = self.get( self.getContextRoot() + '/rootservices' )
        return content
