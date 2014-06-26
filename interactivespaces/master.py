#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mixin import Communicable
from exception import MasterException
from misc import Logger
from live_activity import LiveActivity
from activity import Activity
from live_activity_group import LiveActivityGroup
from space import Space
from space_controller import SpaceController


class Master(Communicable):
    def __init__(self, host=None, port=None, prefix=None):
        """ 
            Instantiate the Master class with host and port only.
            Communication layer and route logic should be inherited from somewhere else
        """
        if host is None:
            self.host = 'lg-head'
        else:
            self.host = host
        if prefix is None:
            self.prefix = '/interactivespaces'
        else:
            self.prefix = prefix
        if port is None:
            self.port = '8080'
        else:
            self.port = port
        self.class_name = 'Master'
        self.log = Logger().get_logger()
        """Add communication layer to master"""
        super(Master, self).__init__()
        self.uri = self._compose_uri(self.host, self.port, self.prefix)

    def get_activities(self, pattern=None):
        """
            Retrieves a list of activities.
            @return array of Activity objects
        """
        activities = []
        url = self._compose_url(class_name='Master', method_name='get_activities', uri=self.uri)
        self.log.info("Trying to retrieve url=%s" % url)
        response = self._api_get_json(url)
        self.log.debug('Got response for "get_activities" %s ' % str(response))
        for activity_data in response:
            activities.append(Activity(activity_data, self.uri))
        return activities
        
    
    def get_live_activities(self, pattern=None):
        """
            Retrieves a list of LiveActivity objects
            @return array of LiveActivity objects
        """
        live_activities = []
        url = self._compose_url(class_name='Master', method_name='get_live_activities', uri=self.uri)
        self.log.info("Trying to retrieve url=%s" % url)
        response = self._api_get_json(url)
        self.log.debug('Got response for "get_live_activities" %s ' % str(response))
        for live_activity_data in response:
            live_activities.append(LiveActivity(live_activity_data, self.uri)) 
        return live_activities
        

    def get_live_activity_groups(self, pattern=None):
        """
            Retrieves a list of live activity groups.
            @return list of LiveActivityGroup objects
        """
        live_activity_groups = []
        url = self._compose_url(class_name='Master', method_name='get_live_activity_groups', uri=self.uri)
        self.log.info("Trying to retrieve url=%s" % url)
        response = self._api_get_json(url)
        self.log.debug('Got response for "get_live_activity_groups" %s ' % str(response))
        for live_activity_group_data in response:
            live_activity_groups.append(LiveActivityGroup(live_activity_group_data, self.uri)) 
        return live_activity_groups

    def get_spaces(self, pattern=None):
        """
            Retrieves a list of live activity groups.
            @return list of Space objects
        """
        spaces = []
        url = self._compose_url(class_name='Master', method_name='get_spaces', uri=self.uri)
        self.log.info("Trying to retrieve url=%s" % url)
        response = self._api_get_json(url)
        self.log.debug('Got response for "get_spaces" %s ' % str(response))
        for space_data in response:
            spaces.append(Space(space_data, self.uri)) 
        return spaces

    def get_space_controllers(self, pattern=None):
        """
            Retrieves a list of live activity groups.
            @return list of Controller objects
        """
        controllers = []
        url = self._compose_url(class_name='Master', method_name='get_space_controllers', uri=self.uri)
        self.log.info("Trying to retrieve url=%s" % url)
        response = self._api_get_json(url)
        self.log.debug('Got response for "get_controllers" %s ' % str(response))
        for controller_data in response:
            controllers.append(SpaceController(controller_data, self.uri)) 
        return controllers
    
    def activity_exists(self, name, version=None, identifying_name=None):
        """
            Checks whether activity exists
            @param name (mandatory)
            @param version
            @identifying_name
            @return bool
        """
        raise NotImplementedError
    
    def live_activity_exists(self, name, uuid=None, controller_uuid=None):
        """
            Checks whether live_activity exists
            @param name
            @param uuid
            @param controller_uuid
            @return bool
        """
        raise NotImplementedError
            
    def get_named_scripts(self, pattern=None):
        """Retrieves a list of named scripts."""
        raise NotImplementedError

    def new_live_activity(self, name, description, activity, controller):
        """Creates a new live activity."""
        raise NotImplementedError

    def new_live_activity_group(self, name, description, live_activities):
        """Creates a new live activity group."""
        raise NotImplementedError

    def new_space(self, name, description, live_activity_groups, spaces):
        """Creates a new space."""
        raise NotImplementedError

    def new_controller(self, name, description, host_id):
        """Creates a new controller."""
        raise NotImplementedError

    def new_named_script(self, name, description, language, content, scheduled=None):
        """Creates a new named script."""
        raise NotImplementedError