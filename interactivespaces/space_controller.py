#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mixin import Fetchable, Statusable, Shutdownable
from misc import Logger
from serializer import SpaceControllerSerializer
from abstract import Path

class SpaceController(Fetchable, Statusable, Shutdownable):
    """ 
        @summary: Should be responsible for managing live activity groups
    """
    def __init__(self, data_hash=None, uri=None):
        self.log = Logger().get_logger()
        self.class_name = self.__class__.__name__
        super(SpaceController, self).__init__()
        if data_hash==None and uri==None:
            self.log.info("No data provided - assuming creation of new LiveActivity")
        else:
            self.data_hash = data_hash
            self.uri = uri
            self.absolute_url = self._get_absolute_url()
            self.log.info("Instantiated Activity object with url=%s" % self.absolute_url)
    
    def __repr__(self):
        return str(self.data_hash)
       
    def new(self, uri, constructor_args):
        """
            @summary: used to create new space controller through API and set the "uri" so that we
            can operate on this instance of SpaceController right away after .new() returns True
            @param constructor_args: dictionary with following structure: {
                            "space_controller_name" : "mandatory string",
                            "space_controller_description" : "non mandatory string",
                            "space_controller_host_id" : "mandatory string"
                            } 
            @param uri: "http://some_server/prefix (passed by master)" 
            @rtype: new SpaceController object or False
        """
        
        unpacked_arguments = {}
        unpacked_arguments['name'] = constructor_args['space_controller_name']
        unpacked_arguments['description'] = constructor_args['space_controller_description']
        unpacked_arguments['hostId'] = constructor_args['space_controller_host_id']
        unpacked_arguments['_eventId_save'] = 'Save'
        
        self.log.info("Creating new SpaceController with arguments: %s" % unpacked_arguments)
        route = Path().get_route_for('SpaceController', 'new')
        url = "%s%s" % (uri, route)
        request_response = self._api_post_json(url, unpacked_arguments)
        
        if request_response.url:
            self.absolute_url = request_response.url.replace("view.html", "view.json")
            self.fetch()
            self.log.info("Created new SpaceController with url=%s, data_hash is now %s" % (self.absolute_url, self.data_hash))
            return self
        else:
            self.log.info("Created new SpaceController %s but returned False" % self)
            return False
        
    def to_json(self):
        """ 
            Should selected attributes in json form defined by the template
        """
        self.serializer = SpaceControllerSerializer(self.data_hash)
        return self.serializer.to_json()
    
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

    """ Private methods below """
    
    def _get_absolute_url(self):
        live_activity_group_id = self.data_hash['id']
        url = "%s/spacecontroller/%s/view.json" % (self.uri, live_activity_group_id)
        return url      