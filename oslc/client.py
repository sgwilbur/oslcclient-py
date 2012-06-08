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
from jazz import workitem


class OslcClient(object):
    # hard-coded for Form Auth
    # todo: add support for Basic Auth
    def __init__(self, server_url, user, password):
        self.__DEBUG_LEVEL__ = 1
        self.base_url = server_url
       
        self.http = httplib2.Http( disable_ssl_certificate_validation=True )
        self.http.follow_redirects = True
        self.headers = {'content-type': 'text/xml', 'accept': 'application/x-oslc-cm-change-request+xml'}
        
# todo: identify namespace mappings to spec/product versions       
        self.oslc_namespaces = {
                                'rdf'  : 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
                                'dc'   : 'http://purl.org/dc/terms/',
                                'jfs'  : 'http://jazz.net/xmlns/prod/jazz/jfs/1.0/',
                                'jd'   : 'http://jazz.net/xmlns/prod/jazz/discovery/1.0/',
                                'jdb'  : 'http://jazz.net/xmlns/prod/jazz/dashboard/1.0/',
                                'jp06' : 'http://jazz.net/xmlns/prod/jazz/process/0.6/',
                                'jp'   : 'http://jazz.net/xmlns/prod/jazz/process/1.0/',
                                'jtp'  : 'http://jazz.net/xmlns/prod/jazz/jtp/0.6/',
                                'ju'   : 'http://jazz.net/ns/ui#',
                                'ns1'        : 'http://jazz.net/xmlns/prod/jazz/process/1.0/',
                                'oslc'       : 'http://open-services.net/ns/core#',
                                'oslc_cm'    : 'http://open-services.net/xmlns/cm/1.0/',
                                'rtc_cm'     : 'http://jazz.net/xmlns/prod/jazz/rtc/cm/1.0/',
                                'oslc_qm'    : 'http://open-services.net/xmlns/qm/1.0/',
                                'oslc_rm'    : 'http://open-services.net/xmlns/rm/1.0/',
                                'oslc_disc'  : 'http://open-services.net/xmlns/discovery/1.0/',
                                'calm'       : 'http://jazz.net/xmlns/prod/jazz/calm/1.0/',
                                'rdfs'       : 'http://www.w3.org/2000/01/rdf-schema#',
                                'opensearch' : 'http://a9.com/-/spec/opensearch/1.1/',
                                 'atom'      : 'http://www.w3.org/2005/Atom', 
                                }  
     
        response, content = self.http.request( self.base_url + "/authenticated/identity", 'GET', headers=self.headers)
        if response['x-com-ibm-team-repository-web-auth-msg'] != 'authrequired':
            raise Exception("Server error authenticating: " + response.__str__())

        self.headers['cookie']=  response['set-cookie'] 
        self.headers['content-type'] = 'application/x-www-form-urlencoded'
        
        # TODO: Post login information, Jazz uses j_security_check for FORM auth.
        response, content = self.http.request(self.base_url+'/authenticated/j_security_check' , 'POST',
                            headers=self.headers, body=urllib.urlencode({'j_username': user, 'j_password': password}))
        
        # Confirm that we are connected, and can grab the secure resource now      
        response, content = self.http.request( self.base_url + "/authenticated/identity", 'GET', headers=self.headers)
        if response.__contains__('x-com-ibm-team-repository-web-auth-msg'):
            raise Exception("Login was not successful, server response: " + response.__str__() )


    def __login__(self):
        # Grab secured resource to initiate login
        response, content = self.http.request( self.base_url + "/authenticated/identity", 'GET', headers=self.headers)
        
        if response.__contains__('x-com-ibm-team-repository-web-auth-msg'):
        
            if response['x-com-ibm-team-repository-web-auth-msg'] != 'authrequired':
                raise Exception("Server error authenticating: " + response.__str__())
            
            # TODO: Post login information, Jazz uses j_security_check for FORM auth.
            response, content = self.http.request(self.base_url+'/authenticated/j_security_check' , 'POST',
                                headers=self.headers, body=urllib.urlencode({'j_username': self.user, 'j_password': self.password}))
            
            # Confirm that we are connected, and can grab the secure resource now      
            response, content = self.http.request( self.base_url + "/authenticated/identity", 'GET', headers=self.headers)
            
            if response.__contains__('x-com-ibm-team-repository-web-auth-msg'):
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
    def get( url ):
        return  self.get( url, self.headers )

    def get( url, headers ):
        response, content = self.http.request(url, 'GET', headers=headers)
        if response.status != 200:
            raise Exception("OslcClient response status != 200 !!!" + response.__str__() + 'content: ' + content.__str__() )
        return content
  
    def getUrlDoc(self, url):
        self.headers['content-type'] = 'text/xml'
        return self.get( url, self.headers )

    def postRequest(self, url, content, headers ):
        raise Exception("unimplemented")

    def postXML(self, url, contentXML ):
        headers = self.headers
#        headers = {'Content-type': 'application/x-oslc-cm-change-request+xml', 'accept': 'text/xml'}

        response, content = self.http.request(url, 'POST', contentXML, headers=headers)        
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
#  Generic xpath helper
#
    def getElembyXpath(self, document_str, xpath ):
        tree = etree.fromstring( document_str )
        elem = tree.xpath( xpath, namespaces=self.oslc_namespaces )
        return elem

#
# Grab the services discovery document
#
    def getRootServicesDoc(self):
        content = self.getUrlDoc( self.getContextRoot() + '/rootservices' )
        return content

#
# Convenience wrapper to grab catalog URL.
# This seems like overkill since this is static as well
    def getCMCatalogURL(self, rootservices_str ):
        catalogElem = self.getElembyXpath( rootservices_str, '/rdf:Description/oslc_cm:cmServiceProviders/@rdf:resource')
        return catalogElem[0]
    def getCMCatalogDoc(self):
        content = self.getUrlDoc( self.getContextRoot() + '/oslc/workitems/catalog' )
        return content
    
## FIXME: Get on the ServiceProvider with the given name
    def getPAServicesURL(self, catalog_str, paName ):
        catalogElem = self.getElembyXpath( catalog_str, '//oslc_disc:ServiceProvider[dc:title=\''+ paName + '\']/oslc_disc:services/@rdf:resource')
        return catalogElem[0]
    
    def getPAServicesDoc(self, paServicesURL):
        content = self.getUrlDoc( paServicesURL )
        return content
    
    def getPAServicesDocbyName(self, paName ):
        paServicesURL = self.getPAServicesURL( self.getCMCatalogDoc(), paName )
        content = self.getPAServicesDoc(paServicesURL)
        return content
    
#  Get the Create factory URL.  
    def getWICreateURL(self, servicedoc_str ):
        catalogElem = self.getElembyXpath( servicedoc_str, '/oslc_cm:ServiceDescriptor/oslc_cm:changeRequests/oslc_cm:factory[@oslc_cm:default=\'true\']/oslc_cm:url')
        return catalogElem[0].text

# get the CM Simple Query URL
    def getWISimpleQueryURL(self, servicedoc_str ):
        catalogElem = self.getElembyXpath( servicedoc_str, '/oslc_cm:ServiceDescriptor/oslc_cm:changeRequests/oslc_cm:simpleQuery/oslc_cm:url')
        return catalogElem[0].text

#
#  Wrapper to provide a hash of hashes interface to the project area details.
#
    def getProjectAreas(self, catalog_str):
        projectAreas = {}
        projectAreaProviderElems = self.getElembyXpath( catalog_str, '//oslc_disc:ServiceProvider')
        for project in projectAreaProviderElems:
        # Each project has: dc:title/text(), oslc_disc:details/@rdf:resource, oslc_disc:services/@rdf:resource ns1:consumerRegistry/@rdf:resource
            title    = project.xpath('dc:title/text()', namespaces=self.oslc_namespaces )[0]
            details  = project.xpath('oslc_disc:details/@rdf:resource', namespaces=self.oslc_namespaces )[0]
            services = project.xpath('oslc_disc:services/@rdf:resource', namespaces=self.oslc_namespaces )[0]
            consumerRegistry = project.xpath('ns1:consumerRegistry/@rdf:resource', namespaces=self.oslc_namespaces )[0]
            # pull off the end of the details url .../project-areas\/(.*)$/
            matches = re.match( r".*project-areas\/(.*)$", details )
            itemId = matches.group(1)
            projectAreas[title] = { 'itemId' : itemId, 'details' : details, 'services' : services, 'consumerRegistry' : consumerRegistry}
        return projectAreas

#
#  Return a Hash of Hashes wrapper to Team areas.
#
    def getTeamAreas(self, projectId ):
        teamAreas =  {}
        teamAreasDoc_str    = self.getUrlDoc( self.getContextRoot() + '/process/project-areas/' +  projectId + '/team-areas/' )
#        print( teamAreasDoc_str )
        # this xpath needs to be absolute to avoid picking up any children team-areas!!
        teamAreaElems      =  self.getElembyXpath( teamAreasDoc_str, '/jp06:team-areas/jp06:team-area' )

        for team in teamAreaElems:
            name  = team.attrib['{http://jazz.net/xmlns/prod/jazz/process/0.6/}name']

            archived  = team.xpath('jp06:archived/text()', namespaces=self.oslc_namespaces )[0]
            description  = team.xpath('jp06:description/text()', namespaces=self.oslc_namespaces )
            members_url  = team.xpath('jp06:members-url/text()', namespaces=self.oslc_namespaces )[0]
            modified  = team.xpath('jp06:modified/text()', namespaces=self.oslc_namespaces )[0]
            project_area_url = team.xpath('jp06:project-area-url/text()', namespaces=self.oslc_namespaces )[0]
            roles_url  = team.xpath('jp06:roles-url/text()', namespaces=self.oslc_namespaces )[0]
            summary  = team.xpath('jp06:summary/text()', namespaces=self.oslc_namespaces )
            url  = team.xpath('jp06:url/text()', namespaces=self.oslc_namespaces )[0]

            #TODO: rather than iterate, just grab the child team-area names
            children = team.xpath('jp06:children/jp06:team-area/@jp06:name', namespaces=self.oslc_namespaces )
            
            # pull off the end of the team-area url .../team-areas\/(.*)$/
            matches = re.match( r".*team-areas\/(.*)$", url )
            itemId = matches.group(1)         
            
            teamAreas[ name ] = { 'archived' : archived, 'description' : description, 'children' : children, 'itemId' : itemId,
                                 'members-url' : members_url, 'modified' : modified, 'name' : name,
                                 'project-area-url' : project_area_url, 'roles-url' : roles_url, 'summary': summary, 'url' : url }
            
#            print( teamAreas[ name] )
            
        return teamAreas


    def getMembers(self, membersDoc_str ):
        members = {}
        memberElems = self.getElembyXpath( membersDoc_str, '//jp06:member' )

        for member in memberElems:
            # Each member has: jp06:url/text(), jp06:user-url/text(), //jp06:role-assignment
            url         = member.xpath('jp06:url/text()', namespaces=self.oslc_namespaces )[0]
            user_url    = member.xpath('jp06:user-url/text()', namespaces=self.oslc_namespaces )[0]
            # pull off the end of the user-url .../users\/(.*)$/
            matches = re.match( r".*users\/(.*)$", user_url )
            userId  = matches.group(1)
            userId  = urllib.unquote( userId )  
            
            roleElems = member.xpath('jp06:role-assignments/jp06:role-assignment', namespaces=self.oslc_namespaces )
            roles = {}
            for role in roleElems:
                r_url           = role.xpath('jp06:url/text()', namespaces=self.oslc_namespaces )[0]
                r_role_url      = role.xpath('jp06:role-url/text()', namespaces=self.oslc_namespaces )[0]
                matches         = re.match( r".*role-assignments\/(.*)$", r_url )
                roleId          = matches.group(1)
                roles[ roleId ] = { 'url' : r_url, 'role-url' : r_role_url }    
        
            members[ userId ] = { 'userId' : userId, 'url' : url, 'user-url' : user_url, 'roles' : roles } 
        return members

#
#  Wrapper interface to Project Membership, returns hash of hashes
#   
    def getProjectMembers(self, projectId ):
        membersDoc_str = self.getUrlDoc( self.getContextRoot() + '/process/project-areas/' +  projectId + '/members' )
        members = self.getMembers(membersDoc_str)    
        return members

#
#
#
    def getTeamMembers(self, projectId, teamId ): 
        membersDoc_str = self.getUrlDoc( self.getContextRoot() + '/process/project-areas/' +  projectId + '/team-areas/' + teamId + '/members' )
        members = self.getMembers(membersDoc_str)
        return members
    
# 
# 
#      

    def getWorkItem(self, itemNumber):
        content = self.getUrlDoc( self.getContextRoot() + '/oslc/workitems/'+ itemNumber +'.xml' )
        return content
     
    def getQueryResults(self, paName, query):
#        queryURL = self.getWISimpleQueryURL( self.getPAServicesDocbyName(paName)) + urllib.urlencode( query )
        queryURL = self.getWISimpleQueryURL( self.getPAServicesDocbyName(paName)) + query
        print( queryURL )
        content = self.getUrlDoc( queryURL )
        return content   

    def submitWI(self, paName, wiContent):
        createURL = self.getWICreateURL( self.getPAServicesDocbyName(paName))
        return self.postXML( createURL, wiContent )

