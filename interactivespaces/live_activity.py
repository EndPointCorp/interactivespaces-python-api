#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mixin import Statusable, Fetchable
from exception import LiveActivityException
from serializer import LiveActivitySerializer
from misc import Logger
from abstract import Path

class LiveActivity(Statusable, Fetchable):
    """
        @summary: when called with constructor_args and other vars set to None, new
        LiveActivity will be constructed and available for .save(). When called
        with data_hash and uri, it will bound itself to an existing object in API
        @todo: .new() should return instance of fetched live activity
    """
    def __init__(self, data_hash, uri):
        """
            @param data_hash: should be master API liveActivity json, may be blank
            @param uri: should be a link to "view.json" of the given live activity
        """
        self.log = Logger().get_logger()
        super(LiveActivity, self).__init__()
        if (data_hash==None and uri==None):
            self.log.info("No data provided - assuming creation of new LiveActivity")
        elif (data_hash!=None and uri!=None):
            self.data_hash = data_hash
            self.uri = uri
            self.absolute_url = self._get_absolute_url()
            self.log.info("Instantiated LiveActivity object with url=%s" % self.absolute_url)

    def __repr__(self):
        return str(self.data_hash)
    
    def __str__(self):
        return self.data_hash 
       
    def new(self, uri, new_data_hash):
        """
        @summary: used to create new object in order to be saved by ".save" method
        @note: POST data to send:
            liveActivity.name:some_name
            liveActivity.description:some_description
            activityId:53
            controllerId:2
            _eventId_save:Save
        @param new_data_hash: dict {"live_activity_name" : "", 
                                        "live_activity_description" : "",
                                        "activity_id" : "",
                                        "controller_id" : "",
                                        "uri" : "http://some_server/prefix (passed by master)"
                                        } 
        @rtype: LiveActivity
        """
        self.log.info("Creating new Live Activity with arguments: %s" % new_data_hash)
        route = Path().get_route_for('LiveActivity', 'new')
        url = "%s%s" % (uri, route)
        post_request = self._api_post_json(url, new_data_hash)
        if post_request:
            return True
        else:
            return False

        
    def save(self):
        """
        @rtype: dict
        @return 
        """
        pass
    
    def send_status_refresh(self):
        """ 
            Should use Statusable._send_status_refresh to make Master ask Controller for the
            status of LiveActivity. After that it's good to refresh the object"
            @rtype: bool
        """
        refresh_route = Path().get_route_for('LiveActivity', 'status') % self.data_hash['id']
        if self._send_status_refresh_command(refresh_route):
            self.log("Successfully refreshed status for LiveActivity url=%s" % self.absolute_url) 
            return True
        else:
            return False
    
    def fetch(self):
        """ 
            Should retrieve private data for an object from Master API
        """
        self.data_hash = self._refresh_object(self.absolute_url)
        return self
    
    def to_json(self):
        """ Should selected attributes in json form defined by the template"""
        self.serializer = LiveActivitySerializer(self.data_hash)
        return self.serializer.to_json()
    
    def name(self):
        """ Should return live activity name"""
        return self.data_hash['name']
    
    def status(self):
        """ Should return status that is currently held in the object instance"""
        try:
            status_data = self.data_hash['active']['runtimeState']
            return status_data
        except LiveActivityException("Activity not running or non existent"):
            return "UNKNOWN"
 
    def identifying_name(self):
        """ Should return LiveActivity identifying name """
        return self.data_hash['activity']['identifyingName']
    
    def version(self):
        """ Should return LiveActivity version """
        return self.data_hash['activity']['version']
    
    def id(self):
        """
        @summary: Should return LiveActivity id
        @rtype: string
        """
        return self.data_hash['activity']['id']
       
    """ Private methods below this text """
     
    def _get_absolute_url(self):
        """
        @rtype: string
        """
        activity_id = self.data_hash['id']
        route = Path().get_route_for('LiveActivity', 'view') % activity_id
        url = "%s%s" % (self.uri, route)
        return url  
        
    
    
    
        
