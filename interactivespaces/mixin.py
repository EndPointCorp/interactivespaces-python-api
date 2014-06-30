#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import json
from abstract import Path
from misc import Logger
from exception import CommunicableException
import requests
import urlparse
import os

class Communicable(object):
    def __init__(self):
        """ 
            @summary: Should be responsible for communication with the API
        """
        self.log = Logger().get_logger()
        
    def _compose_url(self, uri, class_name=None, method_name=None, context=None, action=None):
        """ 
            @summary: Should compose URL trying to do that in two steps:
                1. return if object that tries to retrieve the url
                has route that is already staticaly defined
                2. try to compose the custom route on the basis of URL data
            @rtype: string
        """
        if class_name and method_name:
            self.log.info("Composing url for class_name '%s' and method name '%s'" % (class_name, method_name))
            static_route = Path().get_route_for(class_name, method_name)
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
        
    def _urlopen(self, url, data=None):
        """Helper for opening urls."""
        return urllib2.urlopen(url, data)

    def _api_get_json(self, url):
        """
            @summary: Sends a request to the master, returns only the 'data' from response 
            @rtype: dict or bool
        """
        response = urllib2.urlopen(url)
        data = json.loads(response.read())
        
        try:
            out_data = data['data']
        except Exception:
            out_data = None
            
        if data['result'] != 'success':
            self.log.info("Could not retrieve data for URL=%s" % url)
            return False
        
        if out_data:
            return out_data
        else:
            return True   

    def _api_get_html(self, command, query=None):
        """Sends a request to the master, returns the response."""
        raise NotImplementedError

    def _api_post_json(self, url, payload, file_handler=None):
        """
            @summary: Sends data to the master.
            @rtype: string or False
            @param payload: dictionary containing data to send
            @param url: string containing url that we talk to
            @param file_handler: path to local zipfile - if provided, a multi-part
                post will be sent to the URL
        """
        if file_handler:
            head, tail = os.path.split(file_handler.name)
            file_name = tail
            file_content_type = "application/zip"
            files = {"activityFile" : (file_name , file_handler, file_content_type)}
        else:
            files = None
        self.log.info("Doing a POST request to %s with payload %s" %(url, payload))
        session = requests.session()
        get_response = session.get(url)
        query = urlparse.urlparse(get_response.url).query
        cookies = {"JSESSIONID" : session.cookies['JSESSIONID']}
        url = url + "?" + query
        post_response = session.post(url=url, cookies=cookies, data=payload, files=files) 
        if post_response.status_code == 200:
            self.log.info("_api_post_json returned 200 with post_response.url=%s" % post_response.url)
            return post_response
        else:
            self.log.info("_api_post_json returned post_response.status_code %s" % post_response.status_code)
            return False 
         
    def _api_post_html(self, command, query=None, data=None):
        """Sends data to the master."""
        raise NotImplementedError
    
    def json_raw(self):
        """
        @summary: returns raw unformatted/unmapped json from Master API
        @rtype: dict
        """
        return self.data


class Statusable(Communicable):
    """ 
        @summary: Should be responsible for _refreshing_ status of the object,
        which means that it will send "status" command to IS Controllers.
        In order to fetch the fresh and most up-to-date status you should use 
        .fetch() method on the object.
    """
    
    def __init__(self):
        self.log = Logger().get_logger()
        super(Statusable, self).__init__()
      
    def send_status_refresh_command(self):
        """
            @summary: extracts self.data_hash and self.class_name from children class
                and finds out to which route send GET request to ands sends it
        """
        refresh_route = Path().get_route_for(self.class_name, 'status') % self.data_hash['id']
        if self._send_status_refresh_command(refresh_route):
            self.log.info("Successfully refreshed status for LiveActivity url=%s" % self.absolute_url) 
            return True
        else:
            return False
          
    def _send_status_refresh_command(self, refresh_route):
        """ 
            @summary: Should tell master to retrieve status info from controller
            so master has the most up to date info from the controller
            @param refresh_route: status.json route for specific class
            @rtype: bool
        """
        url = "%s%s" % (self.uri, refresh_route)
        self.log.info("Sending status refresh to url=%s" %url)
        try:
            response = self._api_get_json(url)
        except urllib2.HTTPError, e:
            response = None
            self.log.error("Could not send status refresh because %s" % e)
        if response:
            return True
        else:
            return False

class Fetchable(Communicable):
    """ 
        @summary: Should be responsible for fetching most up to date data from API
    """
    def __init__(self):
        super(Fetchable, self).__init__()
        
    def _refresh_object(self, url):
        """ 
            @summary: Should retrieve fresh data from API
            @param url: string defining from which url to fetch the data 
        """
        self.log.info("Refreshing object for url=%s" % url)
        data = self._api_get_json(url)
        if data:
            self.log.info("Successfully refresh object for url=%s" % url)
            return data
        else:
            self.log.info("Could not refresh object for url=%s" % url)
            return False
        
    def fetch(self):
        """ 
            @summary: Should retrieve private data for an object from Master API
        """
        self.data_hash = self._refresh_object(self.absolute_url)

class Deletable(Communicable):
    def __init__(self):
        super(Deletable, self).__init__()
        
    def send_delete(self):
        pass
    
class Shutdownable(Communicable):
    def __init__(self):
        super(Shutdownable, self).__init__()
        
    def send_shutdown(self):
        pass

class Startupable(Communicable):
    def __init__(self):
        super(Startupable, self).__init__()
        
    def send_startup(self):
        pass

class Activatable(Communicable):
    def __init__(self):
        super(Activatable, self).__init__()
        
    def send_activate(self):
        pass

    def send_deactivate(self):
        pass

class Deployable(Communicable):
    def __init__(self):
        super(Deployable, self).__init__()
        
    def send_deploy(self):
        pass

class Configurable(Communicable):
    def __init__(self):
        super(Configurable, self).__init__()
        
    def send_configure(self):
        pass

class Cleanable(Communicable):
    def __init__(self):
        super(Cleanable, self).__init__()
        
    def send_clean_permanent(self):
        pass
    
    def send_clean_temp(self):
        pass

class Editable(Communicable):
    def __init__(self):
        super(Editable, self).__init__()
        
    def set_metadata(self):
        pass
    
    def set_configuration(self):
        pass