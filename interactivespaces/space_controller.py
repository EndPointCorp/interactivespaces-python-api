#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mixin import Fetchable, Statusable, Shutdownable
from misc import Logger
from serializer import SpaceControllerSerializer

class SpaceController(Fetchable, Statusable, Shutdownable):
    """ 
        Should be responsible for managing live activity groups
    """
    def __init__(self, data_hash=None, uri=None):
        self.log = Logger().get_logger()
        self.data_hash = data_hash
        self.uri = uri
        ''' Add all mixins for thingies like api communication, status retrieval etc'''
        self.absolute_url = self.get_absolute_url()
        self.log.info("Instantiated Activity object with url=%s" % self.absolute_url)
        super(SpaceController, self).__init__()
    
    def to_json(self):
        """ 
            Should selected attributes in json form defined by the template
        """
        self.serializer = SpaceControllerSerializer(self.data_hash)
        return self.serializer.to_json()
    
    def get_absolute_url(self):
        live_activity_group_id = self.data_hash['id']
        url = "%s/spacecontroller/%s/view.json" % (self.uri, live_activity_group_id)
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
  
    def description(self):
        """ Should return Activity description """
        return self.data_hash['description']    
    
    def mode(self):
        """ Should return Activity description """
        return self.data_hash['mode']    
    