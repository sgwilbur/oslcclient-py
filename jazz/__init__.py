__author__ = 'sgwilbur'

import requests
# quiet warnings for self-signed certificates
requests.packages.urllib3.disable_warnings()

class connection(object):

    def __init__(self, server_url, user, password):
        self.__DEBUG_LEVEL__ = 1
        self.base_url = server_url
        self.auth_uri =  '/authenticated/identity'

        self.session = requests.Session()

        self.session.verify = False
        self.session.allow_redirects = True
        self.session.headers = {'accept':'application/xml'}

        self.session.auth = (user, password)

        # print "Initial request for authenticated resource as a challenge."
        login_response = self.session.get(self.base_url + self.auth_uri)
        # print " %s : %s" % ( login_response.status_code,  login_response.headers )

        # hard-coded for Form Auth
        # todo: add support for Basic Auth

        # All responses return HTTP 200 even if you are not authorized, need to check for header to
        # determine if you are logged in, or need to login:
        # x-com-ibm-team-repository-web-auth-msg: authrequired
        if 'x-com-ibm-team-repository-web-auth-msg' in login_response.headers:
            # Form response
            # print "Sending login POST"
            login_response = self.session.post(self.base_url + '/j_security_check', data={ 'j_username': user, 'j_password': password } )
            # print " %s : %s" % ( login_response.status_code,  login_response.headers )

        # If we are still not logged in, then assume we have bad credentials and raise Exception
        if 'x-com-ibm-team-repository-web-auth-msg' in login_response.headers:
            raise Exception( "Cannot login to RTC, invalid credentials" )

    def get_session( self ):
        return self.session

    def get( self, url, headers ):
        return self.session.get( url, headers=headers )

    def put( self, url, data ):
        return self.session.put( url, data )

    def post( self, url, data ):
        return self.session.put( url, data )
