#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mixin import Fetchable, Statusable, Shutdownable, Startupable, Configurable, Deployable 
from misc import Logger
from serializer import LiveActivityGroupSerializer

class LiveActivityGroup(Fetchable, Statusable, Shutdownable, Startupable, Configurable, Deployable):
    """ 
        Should be responsible for managing live activity groups
    """
    def __init__(self, data_hash, uri, name=None, ):
        self.log = Logger().get_logger()
        self.data_hash = data_hash
        self.uri = uri
        ''' Add all mixins for thingies like api communication, status retrieval etc'''
        self.absolute_url = self.get_absolute_url()
        self.log.info("Instantiated Activity object with url=%s" % self.absolute_url)

        super(LiveActivityGroup, self).__init__()
    
        
    def to_json(self):
        """ 
            Should selected attributes in json form defined by the template
        """
        self.serializer = LiveActivityGroupSerializer(self.data_hash)
        return self.serializer.to_json()
    
    def create(self, live_activity_group_name, live_activity_names):
        """
            Should be responsible for creating
            @param live_activity_group_name string
            @param live_activity_names list of existing names
        """
        raise NotImplementedError
    
    def get_absolute_url(self):
        live_activity_group_id = self.data_hash['id']
        url = "%s/liveactivitygroup/%s/view.json" % (self.uri, live_activity_group_id)
        return url  
    
    def fetch(self):
        """ 
            Should retrieve fresh data for the object from Master API
        """
        self.data_hash = self._refresh_object(self.absolute_url)
    
    def id(self):
        return self.data_hash['id']
    
    def name(self):
        """ Should return live activity name"""
        return self.data_hash['name']  
   
    def live_activities(self):
        """ Should return live activity name"""
        live_activities = []
        data = self.data_hash['liveActivities']
        for live_activity in data:
            live_activity_group_live_activity = {"id" : live_activity['id'], 
                                                "description" : live_activity['description'],
                                                "name" : live_activity['name']
                                                }
            live_activities.append(live_activity_group_live_activity)
        return live_activities
  
    def description(self):
        """ Should return Activity description """
        return self.data_hash['description']    