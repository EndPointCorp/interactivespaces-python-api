#!/usr/bin/env python
# -*- coding: utf-8 -*-

from misc import Logger
from mixin import Fetchable
from serializer import ActivitySerializer
from abstract import Path

class Activity(Fetchable):
    """ 
        @summary: Should be responsible for managing a single activity
    """
    def __init__(self, data_hash=None, uri=None, activity_archive_uri=None, name=None):
        self.log = Logger().get_logger()
        super(Activity, self).__init__()
        
        if (data_hash==None and uri==None):
            self.log.info("No data provided - assuming creation of new Activity")
        elif (data_hash!=None and uri!=None):
            self.data_hash = data_hash
            self.uri = uri
            self.absolute_url = self._get_absolute_url()
            self.log.info("Instantiated Activity object with url=%s" % self.absolute_url)
        
    def __repr__(self):
        return str(self.data_hash)
    
    def new(self, uri, constructor_args):
        """
            @summary: method to keep naming convention of .new() methods
        """
        
        new_activity = self.upload(uri, constructor_args['zip_file_handler'])
        return new_activity
    
    def upload(self, uri, zip_file_handler):
        """ 
            @summary: Should make a deployment of the activity with followin steps:
                - receive handler to a local zipfile
                - upload it to the API  
                - save
                - set instance variables for the object
            @return: False or URL to a new Activity
            @param uri: stirng
            @param zip_file_handler: 'file' class instance
            @rtype: new Activity object or False
        """
        self.log.info("Uploading new Activity from file %s" % zip_file_handler)
        route = Path().get_route_for('Activity', 'upload')
        url = "%s%s" % (uri, route)
        payload = {"_eventId_save" : "Save"}
        request_response = self._api_post_json(url, payload, zip_file_handler)
        
        if request_response.url:
            self.absolute_url = request_response.url.replace("view.html", "view.json")
            self.fetch()
            self.log.info("Created new Activity with url=%s, data_hash is now %s" % (self.absolute_url, self.data_hash))
            return self
        else:
            self.log.info("Created new Activity %s but returned False" % self)
            return False
    
        
    def to_json(self):
        """ 
            Should selected attributes in json form defined by the template
        """
        self.serializer = ActivitySerializer(self.data_hash)
        return self.serializer.to_json()
    
    def fetch(self):
        """ Should retrieve data from Master API"""
        self.data_hash = self._refresh_object(self.absolute_url)
    
    def name(self):
        """ Should return live activity name"""
        return self.data_hash['activity']['name']  
    
    def identifying_name(self):
        """ Should return identifying name """
        return self.data_hash['activity']['identifyingName']
    
    def version(self):
        """ Should return Activity version """
        return self.data_hash['activity']['version']
    
    def id(self):
        """ Should return Activity id """
        return self.data_hash['activity']['id']
  
    def description(self):
        """ Should return Activity description """
        return self.data_hash['activity']['description']
    
    """ Private methods below"""
    
    def _get_absolute_url(self):
        activity_id = self.data_hash['id']
        url = "%s/activity/%s/view.json" % (self.uri, activity_id)
        return url  