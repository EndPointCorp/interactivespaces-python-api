#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import json
import time
from abstract import Path
from misc import CommunicationLogger
from exception import CommunicableException

class Communicable(object):
    def __init__(self, post_data=None):
        """
            - post_data in json format
            - host e.g. 'lg-head' or '1.2.3.4'
            - port e.g. 8080
            - location e.g. /interactivespaces/space/all.html
        """
        self.post_data = post_data
        self.log = CommunicationLogger().get_logger()
        self.paths = Path()
        
    def _compose_url(self, uri, class_name=None, method_name=None, context=None, action=None):
        """ Should compose URL trying to do that in two steps:
            1. return if object that tries to retrieve the url
            has route that is already staticaly defined
            2. try to compose the custom route on the basis of URL data
        """
        if class_name and method_name:
            self.log.info("Composing url for class_name '%s' and method name '%s'" % (class_name, method_name))
            static_route = self.paths.get_route_for(class_name, method_name)
            if static_route : 
                self.log.info("Returned auto url %s" % (static_route))
                url = "%s%s" % (uri, static_route)
                return url
            
        elif context and action:
            url = "%s%s%s" % (uri, context, action)
            self.log.info("Composed url %s" % (url))
            return url
        else:
            self.log.info("Could not compose an url.")
            raise CommunicableException
    
    def _compose_uri(self, host, port, prefix):
        uri = "http://%s:%s%s" % (self.host, self.port, prefix)
        return uri
        
    def _urlopen(self, url, data=None):
        """Helper for opening urls."""
        return urllib2.urlopen(url, data)

    def _api_get_json(self, url):
        """Sends a request to the master, returns the response data."""
        response = urllib2.urlopen(url)
        data = json.loads(response.read())
        if data['result'] != 'success':
            self.log.info("Could not retrieve data for URL=%s" % url)
            raise CommunicableException
        return data      

    def _api_get_html(self, command, query=None):
        """Sends a request to the master, returns the response."""
        raise NotImplementedError

    def _api_post_json(self, command, query=None, data=None):
        """Sends data to the master."""
        raise NotImplementedError

    def _api_post_html(self, command, query=None, data=None):
        """Sends data to the master."""
        raise NotImplementedError


class Statusable(Communicable):
    def __init__(self):
        super(Statusable, self).__init__()
        
    def get_status(self):
        pass