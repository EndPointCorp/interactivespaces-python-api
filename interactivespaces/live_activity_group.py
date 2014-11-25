#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mixin import Fetchable, Statusable, Shutdownable, Startupable
from mixin import Deletable, Activatable, Configurable, Metadatable
from mixin import Deployable
from misc import Logger
from serializer import LiveActivityGroupSerializer
from abstract import Path
from live_activity import LiveActivity

class LiveActivityGroup(Fetchable, Statusable, Deletable, Shutdownable,
                        Startupable, Activatable, Configurable, Metadatable,
                        Deployable):
    """
    Should be responsible for managing single live activity group
    """
    def __init__(self, data_hash=None, uri=None):
        self.log = Logger().get_logger()
        self.class_name = self.__class__.__name__
        super(LiveActivityGroup, self).__init__()
        if data_hash==None and uri==None:
            self.log.info("No data_hash and uri provided for LiveActivityGroup constructor, assuming creation")
        else:
            self.data_hash = data_hash
            self.uri = uri
            self.absolute_url = self._get_absolute_url()
            self.log.info("Instantiated Activity object with url=%s" % self.absolute_url)

    def __repr__(self):
        return str(self.data_hash)

    def new(self, uri, constructor_args):
        """
        Used to create new live activity group through API and set the "uri" so that we
        can operate on this instance of LiveActivityGroup right away after .new() returns True
        
        :param constructor_args: dictionary with following structure::
        
            {\
            'liveActivityGroup.name' : 'live_activity_group_name',\
            'liveActivityGroup.description' : 'live_activity_group_description',\
            '_eventId_save' : 'Save',\
            'liveActivityIds' : [1,2,666]\
            }
        
        :param uri: "http://some_server/prefix" (passed by master)
        
        :rtype: new LiveActivityGroup object or False
        """

        self.log.info("Creating new LiveActivityGroup with arguments: %s" % constructor_args)
        route = Path().get_route_for('LiveActivityGroup', 'new')
        url = "%s%s" % (uri, route)
        request_response = self._api_post_json(url, constructor_args)
        if request_response.url:
            self.absolute_url = request_response.url.replace("view.html", "view.json")
            self.fetch()
            self.log.info("Created new LiveActivityGroup with url=%s, data_hash is now %s" % (self.absolute_url, self.data_hash))
            return self
        else:
            self.log.info("Created new LiveActivityGroup %s but returned False" % self)
            return False

    def set_live_activities(self, live_activities_list):
        """
        Used to set new live activities list
        
        :param: dictionary with following structure::
    
            {\
            'liveActivityGroup.name' : 'live_activity_group_name',\
            'liveActivityIds' : [1,2,666]\
            }
            
        :param uri: "http://some_server/prefix" (passed by master)
        
        :rtype: new LiveActivityGroup object or False
        """
        params = { 'liveActivityGroup.name' : self.name(),
                   'liveActivityIds' : live_activities_list,
                   'liveActivityGroup.description' : self.description()
                 }
        self.log.info("Updating LiveActivityGroup with arguments: %s" % params)
        route = Path().get_route_for('LiveActivityGroup', 'edit') % self.id()
        url = "%s%s" % (self.uri, route)
        request_response = self._api_post_json_no_cookies(url, params)
        if request_response.url:
            self.absolute_url = request_response.url.replace("view.html", "view.json")
            self.fetch()
            self.log.info("Updated LiveActivityGroup with url=%s, data_hash is now %s" % (self.absolute_url, self.data_hash))
            return self
        else:
            self.log.info("Updated LiveActivityGroup %s but returned False" % self)
            return False

    def to_json(self):
        """
        Should selected attributes in json form defined by the template
        """
        self.serializer = LiveActivityGroupSerializer(self.data_hash)
        return self.serializer.to_json()

    def id(self):
        return self.data_hash['id']

    def name(self):
        """ Should return live activity group name"""
        return self.data_hash['name']

    def live_activities(self):
        """ Should return list of live LiveActivity instances"""
        live_activities = []
        data = self.data_hash['liveActivities']
        for live_activity_data in data:
            try:
                status = live_activity_data['active']['runtimeState']
            except Exception:
                status = 'UNKNOWN'
            live_activity_group_live_activity = LiveActivity(data_hash=live_activity_data, uri=self.uri)
            live_activities.append(live_activity_group_live_activity)
        return live_activities

    def description(self):
        """ Should return Live Activity Group description """
        return self.data_hash['description']

    """ Private methods below """

    def metadata(self):
        """ Should return Live Activity Group metadata """
        return self.data_hash['metadata']

    def url_id(self):
        """ Returns ID for use in URL for this unique object """
        return live_activity_group_id
