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
from helper import SearchPattern, Searcher

class Master(Communicable):
    """
        @summary: This is the main class with all the logic needed for 
        high level stuff. You will typically use instance of Master for all your scripts.
    """
    def __init__(self, host='lg-head', port='8080', prefix='/interactivespaces'):
        """ 
            @param host: default value is lg-head 
            @param port: default value is 8080
            @param prefix: default value is /interactivespaces
            @todo: refactor filter_* methods because they're not DRY
        """
        self.host, self.port, self.prefix = host, port, prefix
        self.log = Logger().get_logger()
        self.uri = "http://%s:%s%s" % (self.host, self.port, prefix)
        super(Master, self).__init__()
        
    def get_activities(self, search_pattern=None):
        """
            Retrieves a list of Activity objects
            @rtype: list
            @param search_pattern: dictionary of regexps used for searching through Activities
                - example regexp dict: {
                                        "activity_name" : "regexp",
                                        "activity_version" : "regexp" 
                                        }
                - every search_pattern dictionary key may be blank/null
        """
        url = self._compose_url(class_name='Master', method_name='get_activities', uri=self.uri)
        self.log.info("Trying to retrieve url=%s" % url)
        response = self._api_get_json(url)
        self.log.info('Got response for "get_activities" %s ' % str(response))
        self.log.info('get_activities returned %s objects' % str(len(response)))
        activities = self._filter_activities(response, search_pattern)
        return activities

    def get_activity(self, search_pattern=None):
        """
            Retrieves a list of Activity objects
            @rtype: list
            @param search_pattern: dictionary of regexps used for searching through Activities
                - example regexp dict: {
                                        "activity_name" : "regexp",
                                        "activity_version" : "regexp" 
                                        }
                - every search_pattern dictionary key may be blank/null
        """
        url = self._compose_url(class_name='Master', method_name='get_activities', uri=self.uri)
        self.log.info("Trying to retrieve url=%s" % url)
        response = self._api_get_json(url)
        self.log.info('Got response for "get_activities" %s ' % str(response))
        self.log.info('get_activities returned %s objects' % str(len(response)))
        activity = self._filter_activities(response, search_pattern)
        if len(activity) > 1:
            raise MasterException("get_activity returned more than one row (%s)" % len(activity))
        elif isinstance(activity[0], Activity):
            activity[0].fetch()
            self.log.info("get_activity returned Activity:%s" % str(activity))
            return activity
        else:
            raise MasterException("Could not get specific activity for given search pattern")
    
    def get_live_activities(self, search_pattern=None):
        """
            Retrieves a list of LiveActivity objects
            @rtype: list
            @param search_pattern: dictionary of regexps used for searching through LiveActivity names
                - example regexp dict: {
                                        "live_activity_name" : "regexp",
                                        "space_controller_name" : "regexp"
                                        }
                - each search_pattern dictionary key may be blank/null
        """
        url = self._compose_url(class_name='Master', method_name='get_live_activities', uri=self.uri)
        self.log.info("Trying to retrieve url=%s" % url)
        response = self._api_get_json(url)
        self.log.debug('Got response for "get_live_activities" %s ' % str(response))
        self.log.info('get_live_activities returned %s objects' % str(len(response)))
        live_activities = self._filter_live_activities(response, search_pattern)
        return live_activities
    
    def get_live_activity(self, search_pattern=None):
        """
            Retrieves a list of LiveActivity objects
            @rtype: LiveActivity or False
            @param search_pattern: dictionary of regexps used for searching through LiveActivity names
                - example regexp dict: {
                                        "live_activity_name" : "GE ViewSync Master on Node A",
                                        "space_controller_name" : "ISCtlDispAScreen00"
                                        }
                - each search_pattern dictionary key may be blank/null
        """
        url = self._compose_url(class_name='Master', method_name='get_live_activities', uri=self.uri)
        self.log.info("Trying to retrieve url=%s" % url)
        response = self._api_get_json(url)
        self.log.debug('Got response for "get_live_activities" %s ' % str(response))
        self.log.info('get_live_activities returned %s objects' % str(len(response)))
        live_activity = self._filter_live_activities(response, search_pattern)
        if len(live_activity) > 1:
            raise MasterException("get_live_activity returned more than one row (%s)" % len(live_activity))
        elif isinstance(live_activity[0], LiveActivity):
            live_activity[0].fetch()
            self.log.info("get_live_activity returned LiveActivity:%s" % live_activity)
            return live_activity[0]
        else:
            raise MasterException("Could not get specific live activity for given search pattern")

    
    def get_live_activity_groups(self, search_pattern=None):
        """
            Retrieves a list of live activity groups.
            @rtype: list
            @param search_pattern: dictionary of regexps used for searching through LiveActivity names
                - example regexp dict: {
                                        "live_activity_group_name" : "regexp"
                                        }
        """
        url = self._compose_url(class_name='Master', method_name='get_live_activity_groups', uri=self.uri)
        self.log.info("Trying to retrieve url=%s" % url)
        response = self._api_get_json(url)
        self.log.debug('Got response for "get_live_activity_groups" %s ' % str(response))
        self.log.info('get_live_activity_groups returned %s objects' % str(len(response)))
        live_activity_groups = self._filter_live_activity_groups(response, search_pattern)
        return live_activity_groups
    
    def get_live_activity_group(self, search_pattern=None):
        """
            Retrieves a list of live activity groups.
            @rtype: list
            @param search_pattern: dictionary of regexps used for searching through LiveActivity names
                - example regexp dict: {
                                        "live_activity_group_name" : "regexp"
                                        }
        """
        url = self._compose_url(class_name='Master', method_name='get_live_activity_groups', uri=self.uri)
        self.log.info("Trying to retrieve url=%s" % url)
        response = self._api_get_json(url)
        self.log.debug('Got response for "get_live_activity_groups" %s ' % str(response))
        self.log.info('get_live_activity_groups returned %s objects' % str(len(response)))
        live_activity_group = self._filter_live_activity_groups(response, search_pattern)
        if len(live_activity_group) > 1:
            raise MasterException("get_live_activity_group returned more than one row (%s)" % len(live_activity_group))
        elif isinstance(live_activity_group[0], LiveActivityGroup):
            live_activity_group[0].fetch()
            self.log.info("get_live_activity_group returned LiveActivityGroup:%s" % str(live_activity_group))
            return live_activity_group[0]
        else:
            raise MasterException("Could not get specific live activity group for given search pattern")

    def get_spaces(self, search_pattern=None):
        """
            @summary: Retrieves a list of live activity groups.
            @rtype: list
            @param search_pattern: dictionary containing space name regexp
                - example regexp dict: {"space_name" : "regexp"}
        """
        url = self._compose_url(class_name='Master', method_name='get_spaces', uri=self.uri)
        self.log.info("Trying to retrieve url=%s" % url)
        response = self._api_get_json(url)
        self.log.debug('Got response for "get_spaces" %s ' % str(response))
        spaces = self._filter_spaces(response, search_pattern)
        return spaces
    
    def get_space(self, search_pattern=None):
        """
            @summary: Retrieves a Space
            @rtype: Space
            @param search_pattern: dictionary containing space name regexp
                - example regexp dict: {"space_name" : "regexp"}
        """
        url = self._compose_url(class_name='Master', method_name='get_spaces', uri=self.uri)
        self.log.info("Trying to retrieve url=%s" % url)
        response = self._api_get_json(url)
        self.log.debug('Got response for "get_spaces" %s ' % str(response))
        space = self._filter_spaces(response, search_pattern)
        if len(space) > 1:
            raise MasterException("get_space returned more than one row (%s)" % len(space))
        elif isinstance(space[0], Space):
            space[0].fetch()
            self.log.info("get_space returned Space:%s" % str(space))
            return space[0]
        else:
            raise MasterException("Could not get specific space for given search pattern")

    def get_space_controllers(self, search_pattern=None):
        """
            Retrieves a list of live space controllers.
            @rtype: list
            @param search_pattern: dictionary containing regexps and strings
                - example regexp dict: {
                                        "state" : "STRING",
                                        "mode" : "STRING",
                                        "name" : "regexp",
                                        "uuid" : "STRING"
                                        }
        """
        url = self._compose_url(class_name='Master', method_name='get_space_controllers', uri=self.uri)
        self.log.info("Trying to retrieve url=%s" % url)
        response = self._api_get_json(url)
        self.log.debug('Got response for "get_controllers" %s ' % str(response))
        space_controllers = self._filter_space_controllers(response, search_pattern)
        return space_controllers

    def get_space_controller(self, search_pattern=None):
        """
            Retrieves a list of live space controllers.
            @rtype: SpaceController
            @param search_pattern: dictionary containing regexps and strings
                - example regexp dict: {
                                        "space_controller_state" : "STRING",
                                        "space_controller_mode" : "STRING",
                                        "space_controller_name" : "regexp",
                                        "space_controller_uuid" : "STRING"
                                        }
        """
        url = self._compose_url(class_name='Master', method_name='get_space_controllers', uri=self.uri)
        self.log.info("Trying to retrieve url=%s" % url)
        response = self._api_get_json(url)
        self.log.debug('Got response for "get_controllers" %s ' % str(response))
        space_controller = self._filter_space_controllers(response, search_pattern)
        if len(space_controller) > 1:
            raise MasterException("get_space_controller returned more than one row")
        elif isinstance(space_controller[0], SpaceController):
            space_controller[0].fetch()
            self.log.info("get_space_controller returned SpaceController:%s" % str(space_controller))
            return space_controller[0]
        else:
            raise MasterException("Could not get specific space controller for given search pattern")
        
    def get_named_scripts(self, pattern=None):
        """Retrieves a list of named scripts."""
        raise NotImplementedError

    def new_live_activity(self, constructor_args):
        """
            @summary: creates a new live activity and returns it
            @param constructor_args: - dictionary containing all of below keys:
                {
                "live_activity_name": "string containing name of a new live activity (mandatory)"
                "live_activity_description" : "string containing description" 
                "activity_name" : "string containing activity name"
                "space_controller_name" : "string containing controller name"
                }
            @rtype: LiveActivity
        """
         
        unpacked_arguments={}
        unpacked_arguments['activityId'] = self.get_activity({"activity_name" : constructor_args['activity_name']}).id()
        unpacked_arguments['controllerId'] = self.get_space_controller({"space_controller_name" : constructor_args['space_controller_name']}).id()
        unpacked_arguments['live_activity_description'] = constructor_args['live_activity_description']
        unpacked_arguments['liveActivity.name'] = constructor_args['live_activity_name']
        unpacked_arguments['_eventId_save'] = 'Save'
        
        activity = LiveActivity().new(self.uri, unpacked_arguments)
        self.log.info("Master:new_live_activity returned activity:%s" % activity)
        return activity
    
    def new_activity(self, constructor_args):
        """
            @summary: creates a new activity and returns it
            @param constructor_args: - dictionary containing all of below keys:
                {
                "zip_file_handler": "zipfile object (mandatory)"
                }
            @rtype: Activity or False
        """ 
        
        activity = Activity().new(self.uri, constructor_args)
        self.log.info("Master:new_activity returned activity:%s" % activity)
        return activity
        
    def new_space_controller(self, constructor_args):
        """
            @summary: creates new controller
            @param constructor_args: dictionary containing all of below keys:
                {
                "space_controller_name" : "mandatory string",
                "space_controller_description" : "non mandatory string",
                "space_controller_host_id" : "mandatory string"
                }
            
        """
        space_controller = SpaceController().new(self.uri, constructor_args)
        return space_controller

    def new_live_activity_group(self, constructor_args):
        """
            @summary: Creates a new live activity group.
            @param constructor_args: dictionary with following structure:
                {
                "live_activity_group_name" : "example.py live_activity_group_name",
                "live_activity_group_description" : "created by example.py",
                "live_activities" : [{"live_activity_name" : "SV Master on Node A",
                "space_controller_name" : "ISCtlDispAScreen00"},
                {"live_activity_name" : "SV Slave 01 on Node A",
                "space_controller_name" : "ISCtlDispAScreen00"}]
                }
        """
        live_activity_ids = self._translate_live_activities_names_to_ids(constructor_args['live_activities'])
        unpacked_arguments = {}
        unpacked_arguments['liveActivityGroup.name'] = constructor_args['live_activity_group_name']
        unpacked_arguments['liveActivityGroup.description'] = constructor_args['live_activity_group_description']
        unpacked_arguments['_eventId_save'] = 'Save'
        unpacked_arguments['liveActivityIds'] = live_activity_ids

        live_activity_group = LiveActivityGroup().new(self.uri, unpacked_arguments)
        return live_activity_group
    
    def new_space(self, name, description, live_activity_groups, spaces):
        """Creates a new space."""
        raise NotImplementedError

    def new_controller(self, name, description, host_id):
        """Creates a new controller."""
        raise NotImplementedError

    def new_named_script(self, name, description, language, content, scheduled=None):
        """Creates a new named script."""
        raise NotImplementedError
    
    """ Private methods below """
    
    def _filter_live_activities(self, response, search_pattern):
        """
        @summary: Should iterate over response from Master API and filter
        live activites with regards to their name"
        @param response: response['data'] from master API
        @param search_pattern: dictionary where values may be regexps
        @todo: refactor filtering because it looks ugly and make it global for all classes
        """
        live_activities = []
        """ Make a search pattern with default values set to None"""
        if isinstance(search_pattern, dict):
            search_pattern = SearchPattern(search_pattern)
        else:
            search_pattern = SearchPattern()
        
        live_activity_name = search_pattern['live_activity_name']
        
        """ Nested values are returning exception so do it manually here """
        try:
            space_controller_name = search_pattern['controller']['name']
        except Exception:
            space_controller_name = None
        
        self.log.debug("Filtering activities with pattern=%s" % search_pattern)
        
        for live_activity_data in response:
            do_filter = True
            """ Var for holding the state of filtering """
            current_live_activity_name = live_activity_data['name']
            current_space_controller_name = live_activity_data['controller']['name']
            if space_controller_name and do_filter:
                if Searcher().match(current_space_controller_name, space_controller_name):
                    pass
                else:
                    do_filter = False 
            if live_activity_name and do_filter:
                if Searcher().match(current_live_activity_name, live_activity_name):
                    pass
                else:
                    do_filter = False  
            if do_filter==True:
                live_activities.append(LiveActivity(live_activity_data, self.uri)) 
        self.log.info("Filtered live_activities and returned %s object(s)" % str(len(live_activities)))
        return live_activities
    
    def _filter_activities(self, response, search_pattern):
        """
        @summary: Should iterate over response from Master API and filter
        live activites with regards to their name"
        @param response: response['data'] from master API
        @param search_pattern: dictionary where values may be regexps
        @rtype: list of Activity objects
        
        """
        activities = []
        """ Make a search pattern with default values set to None"""
        if isinstance(search_pattern, dict):
            search_pattern = SearchPattern(search_pattern)
        else:
            search_pattern = SearchPattern()
            
        activity_name = search_pattern['activity_name']
        activity_version = search_pattern['activity_version']
        
        self.log.debug("Filtering activities with pattern=%s" % search_pattern)
        
        for activity_data in response:
            do_filter = True
            """ Var for holding the state of filtering """
            current_activity_name = activity_data['name']
            current_activity_version = activity_data['version']
            if activity_version and do_filter:
                if Searcher().match(current_activity_version, activity_version):
                    pass
                else:
                    do_filter = False 
            if activity_name and do_filter:
                if Searcher().match(current_activity_name, activity_name):
                    pass
                else:
                    do_filter = False  
            if do_filter==True:
                activities.append(Activity(activity_data, self.uri)) 
        self.log.info("Filtered activities and returned %s object(s) : %s" % (str(len(activities)), activities))
        return activities
    
    def _filter_live_activity_groups(self, response, search_pattern):
        """
        @summary: Should iterate over response from Master API and filter
        live activity groups with regards to their name"
        @param response: response['data'] from master API
        @param search_pattern: dictionary where values may be regexps
        @rtype: list of LiveActivityGroup objects
        
        """
        live_activity_groups = []
        """ Make a search pattern with default values set to None"""
        if isinstance(search_pattern, dict):
            search_pattern = SearchPattern(search_pattern)
        else:
            search_pattern = SearchPattern()
            
        live_activity_group_name = search_pattern['live_activity_group_name']
        
        self.log.debug("Filtering activities with pattern=%s" % search_pattern)
        
        for live_activity_group_data in response:
            do_filter = True
            """ Var for holding the state of filtering """
            current_live_activity_group_name = live_activity_group_data['name']
            if live_activity_group_name and do_filter:
                if Searcher().match(current_live_activity_group_name, live_activity_group_name):
                    pass
                else:
                    do_filter = False 
            if do_filter==True:
                live_activity_groups.append(LiveActivityGroup(live_activity_group_data, self.uri)) 
        self.log.info("Filtered live_activity_groups and returned %s object(s)" % str(len(live_activity_groups)))
        return live_activity_groups
    
    def _filter_spaces(self, response, search_pattern):
        """
        @summary: Should iterate over response from Master API and filter
        live activity groups with regards to their name"
        @param response: response['data'] from master API
        @param search_pattern: dictionary where values may be regexps
        @rtype: list of Space objects
        
        """
        spaces = []
        """ Make a search pattern with default values set to None"""
        if isinstance(search_pattern, dict):
            search_pattern = SearchPattern(search_pattern)
        else:
            search_pattern = SearchPattern()
            
        space_name = search_pattern['space_name']
        
        self.log.debug("Filtering spaces with pattern=%s" % search_pattern)
        
        for space_data in response:
            do_filter = True
            """ Var for holding the state of filtering """
            current_space_name = space_data['name']
            if space_name and do_filter:
                if Searcher().match(current_space_name, space_name):
                    pass
                else:
                    do_filter = False 
            if do_filter==True:
                spaces.append(Space(space_data, self.uri)) 
        self.log.info("Filtered spaces and returned %s object(s)" % str(len(spaces)))
        return spaces

    def _filter_space_controllers(self, response, search_pattern):
        """
        @summary: Should iterate over response from Master API and filter
            space controllers with regards to the given search dictionary
            consisting of name, uuid, mode and state (none of them are 
            mandatory)"
        @param response: response['data'] from master API
        @param search_pattern: dictionary where values may be regexps
        @rtype: list of Space objects
        
        """
        space_controllers = []
        """ Make a search pattern with default values set to None"""
        if isinstance(search_pattern, dict):
            search_pattern = SearchPattern(search_pattern)
        else:
            search_pattern = SearchPattern()
            
        space_controller_name = search_pattern['space_controller_name']
        space_controller_uuid = search_pattern['space_controller_uuid']
        space_controller_state = search_pattern['space_controller_state']
        space_controller_mode = search_pattern['space_controller_mode']
        
        self.log.debug("Filtering space controllers with pattern=%s" % search_pattern)
        
        for space_controller_data in response:
            do_filter = True
            current_space_controller_name = space_controller_data['name']
            current_space_controller_uuid = space_controller_data['uuid']
            current_space_controller_mode = space_controller_data['mode']
            current_space_controller_state = space_controller_data['state']
            if space_controller_name and do_filter:
                if Searcher().match(current_space_controller_name, space_controller_name):
                    pass
                else:
                    do_filter = False 
            if space_controller_uuid and do_filter:
                if current_space_controller_uuid == space_controller_uuid:
                    pass
                else:
                    do_filter = False 
            if space_controller_mode and do_filter:
                if current_space_controller_mode == space_controller_mode:
                    pass
                else:
                    do_filter = False 
            if space_controller_state and do_filter:
                if current_space_controller_state == space_controller_state:
                    pass
                else:
                    do_filter = False 
            if do_filter==True:
                space_controllers.append(SpaceController(space_controller_data, self.uri)) 
        self.log.info("Filtered space_controllers and returned %s object(s)" % str(len(space_controllers)))
        return space_controllers
    
    def _translate_live_activities_names_to_ids(self, live_activities):
        """
            @param live_activities: list of dictionaries containing following keys:
                { 
                "live_activity_name" : "some_name",
                "space_controller_name" : "some controller name"
                }
            @rtype: list
        """
        live_activity_ids = []
        for la_data in live_activities:
            live_activity = self.get_live_activity(la_data)
            live_activity_ids.append(live_activity.id())
        self.log.info("Translated %s live_activity_names to ids with a result of %s" % (len(live_activity_ids), live_activity_ids) )
        return live_activity_ids