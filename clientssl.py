# Source: http://stackoverflow.com/questions/6277027/suds-over-https-with-cert

import urllib2 as u2
from suds.transport.http import HttpTransport
import httplib, socket

class HTTPSClientAuthHandler(u2.HTTPSHandler):  
    def __init__(self, cert):  
        u2.HTTPSHandler.__init__(self)  
        self.cert = cert

    def https_open(self, req):  
        #Rather than pass in a reference to a connection class, we pass in  
        # a reference to a function which, for all intents and purposes,  
        # will behave as a constructor 
        return self.do_open(self.getConnection, req) 

    def getConnection(self, host, timeout=300):  
        return httplib.HTTPSConnection(host, key_file=self.cert, cert_file=self.cert)  

class HTTPSClientCertTransport(HttpTransport):
    def __init__(self, cert, *args, **kwargs):
        HttpTransport.__init__(self, *args, **kwargs)
        self.cert = cert

    def u2open(self, u2request):
        """
        Open a connection.
        @param u2request: A urllib2 request.
        @type u2request: urllib2.Requet.
        @return: The opened file-like urllib2 object.
        @rtype: fp
        """
        tm = self.options.timeout
        url = u2.build_opener(HTTPSClientAuthHandler(self.cert))  
        if self.u2ver() > 2.6:
            socket.setdefaulttimeout(tm)
            return url.open(u2request)
        else:
            return url.open(u2request, timeout=tm)
