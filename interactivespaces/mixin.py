#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2

class Communicable(object):
    def __init__(self, post_data=None, host, port, context, action):
        ''' must be initiated with:
              - post_data in json format
              - host e.g. 'lg-head' or '1.2.3.4'
              - port e.g. 8080
              - context e.g. 'liveactivity'
              - action e.g. 'all' or 'connect'
          '''
        self.post_data = post_data
        self.host = host
        self.port = port
        self.context = context
        self.action = action
        self.response = None

    def _urlopen(self, url, data=None):
        """Helper for opening urls."""
        return urllib2.urlopen(url, data)

    def _api_get_json(self, command):
        """Sends a request to the master, returns the response data."""
        raise NotImplementedError

    def _api_get_html(self, command, query=None):
        """Sends a request to the master, returns the response."""
        raise NotImplementedError

    def _api_post_json(self, command, query=None, data=None):
        """Sends data to the master."""
        raise NotImplementedError

    def _api_post_html(self, command, query=None, data=None):
        """Sends data to the master."""
        raise NotImplementedError
