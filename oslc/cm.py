'''
Created on August 6th, 2012

@author: swilbur@gmail.com
'''
import urllib
import httplib2
import re
import pprint
from lxml import etree

from exceptions import Exception
from jazz import workitem, projectarea
from oslc.client import OslcClient

class OslcCMClient(OslcClient):
  
  def __init__(self, server_url, user, password):
    OslcClient.__init__(self, server_url, user, password )
    
    
#
# Convenience wrapper to grab catalog URL.
# This seems like overkill since this is static as well
    def getCMCatalogURL(self, rootservices_str ):
        catalogElem = self.getElembyXpath( rootservices_str, '/rdf:Description/oslc_cm:cmServiceProviders/@rdf:resource')
        return catalogElem[0]
        
    def getCMCatalogDoc(self):
        content = self.get( self.getContextRoot() + '/oslc/workitems/catalog' )
        return content
    
## FIXME: Get on the ServiceProvider with the given name
    def getPAServicesURL(self, catalog_str, paName ):
        catalogElem = self.getElembyXpath( catalog_str, '//oslc_disc:ServiceProvider[dc:title=\''+ paName + '\']/oslc_disc:services/@rdf:resource')
        return catalogElem[0]
    
    def getPAServicesDoc(self, paServicesURL):
        content = self.get( paServicesURL )
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

    def getProjectAreaId( self, name ):
        pa_full_url = self.getElembyXpath( self.getCMCatalogDoc() , '//oslc_disc:ServiceProvider[dc:title=\''+ name + '\']/oslc_disc:details/@rdf:resource')[0]
        # https://qwin118.ratl.swg.usma.ibm.com:9445/rtc/process/project-areas/_CyLacK6REeGkk943cytsVw
        # split on '/' and grab the last element in the array which should just be the context id
        pa_context_id = pa_full_url.split('/')[-1]
        return pa_context_id
 #       pa = jazz.projectarea.ProjectArea( name, pa_context_id )
 #       return pa

#
#  Return a Hash of Hashes wrapper to Team areas.
#
    def getTeamAreas(self, projectId ):
        teamAreas =  {}
        teamAreasDoc_str    = self.get( self.getContextRoot() + '/process/project-areas/' +  projectId + '/team-areas/' )
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
        membersDoc_str = self.get( self.getContextRoot() + '/process/project-areas/' +  projectId + '/members' )
        members = self.getMembers(membersDoc_str)    
        return members

#
#
#
    def getTeamMembers(self, projectId, teamId ): 
        membersDoc_str = self.get( self.getContextRoot() + '/process/project-areas/' +  projectId + '/team-areas/' + teamId + '/members' )
        members = self.getMembers(membersDoc_str)
        return members
    
# 
# 
#      

    def getWorkItem(self, itemNumber):
        content = self.get( self.getContextRoot() + '/oslc/workitems/'+ itemNumber +'.xml' )
        return content
     
    def getQueryResults(self, paName, query):
#        queryURL = self.getWISimpleQueryURL( self.getPAServicesDocbyName(paName)) + urllib.urlencode( query )
        queryURL = self.getWISimpleQueryURL( self.getPAServicesDocbyName(paName)) + query
        print( queryURL )
        content = self.get( queryURL )
        return content   

    def submitWI(self, paName, wiContent):
        createURL = self.getWICreateURL( self.getPAServicesDocbyName(paName))
        return self.postXML( createURL, wiContent )