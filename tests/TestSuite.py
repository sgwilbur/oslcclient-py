'''
Created on May 17, 2011

@author: sgw
'''
import unittest
from oslc import client
import pprint, pickle

class TestClient(unittest.TestCase):

    def setUp(self):
        pkl_file = open('creds.pkl', 'rb')
        creds = pickle.load(pkl_file)
        pkl_file.close()
#        pprint.pprint( creds )
        
        self.server = creds['server']
        self.projectName = creds['projectName']
        self.user = creds['user']
        self.passwd = creds['password']
        self.jazz = client.OslcClient('https://'+ self.server + ':9445/rtc', self.user, self.passwd )

    def tearDown(self):
        pass

    def testLoginSuccess(self):
        self.jazz = client.OslcClient('https://'+ self.server + ':9445/rtc', self.user, self.passwd )
        pass
    
    def testLoginFail(self):
        try:
            self.jazz = client.OslcClient('https://'+ self.server + ':9445/rtc', self.user, 'xxx' )
        except Exception:
            pass
    
    def testGetRootServicesDoc(self):
        print( self.jazz.getRootServicesDoc() )
        pass

    def testGetWI(self):
        print( self.jazz.getWorkItem('1') )
        pass

    def testQuery(self):
        print( self.jazz.getQueryResults(self.projectName, '?oslc_cm.query=rtc_cm:com.ibm.rational.utl.request.attrib.old_id=%22CRT00004598%22&oslc_cm.properties=dc:title,dc:identifier,dc:type') )
        pass

    def testSubmitWI(self):
        wiContent ="""<?xml version="1.0" encoding="UTF-8" ?>
<oslc_cm:ChangeRequest xmlns:oslc_cm="http://open-services.net/xmlns/cm/1.0/" xmlns:calm="http://jazz.net/xmlns/prod/jazz/calm/1.0/" xmlns:dc="http://purl.org/dc/terms/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:rtc_cm="http://jazz.net/xmlns/prod/jazz/rtc/cm/1.0/">
<rtc_cm:projectArea rdf:resource="%(server_url)s/oslc/projectareas/%(projectId)s"/>
<rtc_cm:filedAgainst rdf:resource="%(server_url)s/resource/itemOid/com.ibm.team.workitem.Category/%(filedAgainstId)s"/>
<dc:type rdf:resource="%(server_url)s/oslc/types/%(projectId)s/com.ibm.rational.utl.request.type.utlrequest"/>
<rtc_cm:com.ibm.rational.utl.request.attrib.business_justification>This project has a very high visibility. </rtc_cm:com.ibm.rational.utl.request.attrib.business_justification>
<dc:title>Support to assess RTC deployment</dc:title>
<dc:description>Following a first analysis of their SW development process in 2010, we have started an assessment of the environment in order to prepare the deployment of RTC.</dc:description>
</oslc_cm:ChangeRequest>""" % { 'server_url' : 'https://wincqserver:9445/rtc', 'projectId' : '_v-iPIIO2Ed-ec4_ZoGHE4w', 'filedAgainstId' : '_YehX8IVXEd-0pPi2nnFPlA' }
        print( wiContent)

        print( self.jazz.submitWI(self.projectName, wiContent))
        pass

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
