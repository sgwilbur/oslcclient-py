
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import requests
import jazz
import os
import json
import pprint
import re
from lxml import etree
from io import StringIO, BytesIO

class services(object):

    '''
     Setup instance variables for Value Manager Helper class.
    '''
    def __init__(self, jazz_connection):
        self.oslc_namespaces = {
                       'dc' : 'http://purl.org/dc/terms/',
                       'jfs_proc' : 'http://jazz.net/xmlns/prod/jazz/process/1.0/',
                       'oslc_disc': 'http://open-services.net/xmlns/discovery/1.0/',
                       'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'}

        self.conn = jazz_connection
        self.sess = jazz_connection.get_session()
        self.base_url = jazz_connection.base_url

        # locals cached after access
        self.projects = {}
        self.categories = {}

    '''
     Get all project areas and store them in a new local variable self.projects
     which is a dict of Project Areas key'd by name containing services_url, and uuid
    '''
    def get_project_areas(self):

        # if not yet defined load it, otherwise just return it
        if not self.projects:
            self.projects = {}
            # http://stackoverflow.com/questions/15622027/parsing-xml-file-gets-unicodeencodeerror-elementtree-valueerror-lxml
            req = self.sess.get( self.conn.base_url + '/oslc/workitems/catalog.xml',
                            headers={'accept': 'application/xml', 'content-type':'application/xml'},
                            stream=True  )
            req.raw.decode_content = True

            # Get ElementTree ready to parse
            pa_catalog = etree.parse(req.raw)
            #print etree.tostring( pa_catalog )

            # /oslc_dic:ServiceProviderCatalog/oslc_disc:entry/oslc_dic:ServiceProvider
            projects = pa_catalog.xpath('/oslc_disc:ServiceProviderCatalog/oslc_disc:entry/oslc_disc:ServiceProvider', namespaces=self.oslc_namespaces)

            for project in projects:
                #print etree.tostring( project )
                project_area_name = project.xpath('./dc:title/text()', namespaces=self.oslc_namespaces)[0]
               # print "title: ", name

                services_url = project.xpath('./oslc_disc:services/@rdf:resource',  namespaces=self.oslc_namespaces)[0]
                #print services_url
                uuid = re.search('.*/oslc/contexts/(.*)/workitems/.*', services_url).group(1)

                self.projects[project_area_name] = { 'uuid': uuid,
                                                     'services_url ' : services_url,
                                                     'workitem_url' : self.base_url + '/oslc/contexts/'
                                                         + uuid + '/workitems'
                                                     }

        return self.projects

    '''
     Builds on the get_project_areas method above to pull all projects and just
     return the one specified by project name.
    '''
    def get_project_area(self, project_name ):
        if not self.projects:
            self.get_project_areas()

        if project_name not in self.projects:
            raise Exception("ERROR: Did not find project area named: %s" % project_name )

        return self.projects[project_name]

    '''
     Returns all Categories in the application instance
    '''
    def get_all_categories( self ):

        if not self.categories:
            req = self.sess.get( self.conn.base_url + '/oslc/categories',
                    headers={'accept': 'application/json', 'content-type':'application/json'} )

            if req.status_code == 200:
                categories = json.loads( req.text )['oslc_cm:results']
                self.categories = self.add_category_uuid( categories )
                # self.categories = self.__get_sorted_categories( self.categories )
            else:
                raise Exception("ERROR: Failed to get categories.")

        return self.categories

    '''
     Get only Categories for the project specified by name, returns a list of
     dict objects one for each category
    '''
    def get_categories_for_project(self, project_name ):

        # Create a URI for this project area
        specific_project_uri = self.conn.base_url + '/oslc/projectareas/' + self.get_project_area(project_name)['uuid']

        category_query_url = '%s/oslc/categories?oslc_cm.query=rtc_cm:projectArea="%s"' % (self.conn.base_url, specific_project_uri)

        req = self.sess.get( category_query_url, headers={'accept': 'application/json', 'content-type':'application/json'} )

        if req.status_code == 200:
            categories = json.loads( req.text )['oslc_cm:results']
            #pprint.pprint( categories )
            return self.__get_sorted_categories( self.__add_category_uuid( categories ) )
        else:
            raise Exception("ERROR: Failed to get categories for Project %s." % (project_name) )

    '''
     Get only Categories for the project specified by name, add a uuid attribute
     requires iterating over all categories in a list
    '''
    def __add_category_uuid(self, categories ):

        for project in categories:
            #pprint.pprint( project )
            category_url = project['rdf:resource']
            uuid = re.search('.*/resource/itemOid/com.ibm.team.workitem.Category/(.*)$', category_url).group(1)
            project['uuid'] = uuid

        return categories
    '''
     Helper method to sort the categories
    '''
    # TODO: Can I do this in the query with an orderby clause or something ?
    def __get_sorted_categories(self, categories):
        return sorted( categories, key=lambda cat: cat['dc:title'] )

    '''
     Get the values of an enumeration for the project and enum literal specified
    '''
    def get_enum(self, project_name, enum_name):
        req = self.sess.get(
                self.conn.base_url + '/oslc/enumerations/' + self.get_project_area(project_name)['uuid'] +'/'+ enum_name,
                headers={'accept': 'application/json', 'content-type':'application/json'} )

        if req.status_code == 200:
            enum = json.loads( req.text )

        else:
            raise Exception("ERROR: Failed to get enum %s for project name %s" % (enum_name, project_name) )

        return self.__get_sorted_enum( enum )

    '''
     private wrapper for sorting enum lists
    '''
    def __get_sorted_enum(self, enum_values):
        return sorted( enum_values, key=lambda enum: enum['dc:title'] )


    '''
    Unused as I cannot find a reason for parsing the services doc for any urls
    we can not construct the url in a simpler way for...
    '''
    def get_services_doc( self, project_name ):
        pa = self.get_project_area( project_name )

        req = self.sess.get( pa[ services_url ],
                                    headers={'accept': 'application/xml', 'content-type':'application/xml'},
                                    stream=True  )
        req.raw.decode_content = True

        # Get ElementTree ready to parse
        pa_services = etree.parse(req.raw)

        # Interesting things here are the factory urls and query urls for narrow
        # but they are trivial to create if you have the project uuid so not necessary
        # to actually discover them here, just defining them below
        raise Exception( "Unimplemented")

    '''
     Nullified the need for these method by just constructing it and adding it to
     the project object in the projects dict
    '''
    def get_project_query_url( self, project_name ):
        return self.get_project_area( project_name )['workitem_url']
    def get_project_create_url( self, project_name ):
        return self.get_project_area( project_name )['workitem_url']
