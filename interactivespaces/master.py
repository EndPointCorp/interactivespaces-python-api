#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mixin import Communicable
from exception import MasterException, ControllerNotFoundException, ActivityNotFoundException
from exception import LiveActivityNotFoundException, LiveActivityGroupNotFoundException, SpaceNotFoundException
from misc import Logger
from live_activity import LiveActivity
from activity import Activity
from live_activity_group import LiveActivityGroup
from space import Space
from space_controller import SpaceController
from helper import SearchPattern, Searcher

class Master(Communicable):
    """
    This is the main class with all the logic needed for
    high level stuff. You will typically use instance of
    Master for all your scripts.
    """
    def __init__(self, host='lg-head', port='8080', prefix='/interactivespaces', logfile_path='ispaces-client.log'):
        """
        :param host: default value is lg-head
        :param port: default value is 8080
        :param prefix: default value is /interactivespaces
        :todo: refactor filter_* methods because they're not DRY
        """
        self.host, self.port, self.prefix = host, port, prefix
        self.log = Logger(logfile_path=logfile_path).get_logger()
        self.uri = "http://%s:%s%s" % (self.host, self.port, prefix)
        super(Master, self).__init__()

    def get_activities(self, search_pattern=None):
        """
        Retrieves a list of Activity objects

        :rtype: list

        :param search_pattern: dictionary of regexps used for searching through Activities

        example regexp dict::

            {\
            "activity_name" : "regexp"\
            "activity_version" : "regexp"\
            }

        every search_pattern dictionary key may be blank/null
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

        :rtype: list

        :param search_pattern: dictionary of regexps used for searching through Activities

        example regexp dict::

            {\
            "activity_name" : "regexp",\
            "activity_version" : "regexp"\
            }

        every search_pattern dictionary key may be blank/null
        """
        url = self._compose_url(class_name='Master', method_name='get_activities', uri=self.uri)
        self.log.info("Trying to retrieve url=%s" % url)
        response = self._api_get_json(url)
        self.log.info('Got response for "get_activities" %s ' % str(response))
        self.log.info('get_activities returned %s objects' % str(len(response)))
        activity = self._filter_activities(response, search_pattern)

        return self._validate_single_getter_results(activity, Activity, ActivityNotFoundException)

    def get_live_activities(self, search_pattern=None):
        """
        Retrieves a list of LiveActivity objects

        :rtype: list

        :param search_pattern: dictionary of regexps used for searching through LiveActivity names

        example regexp dict::

            {\
            "live_activity_name" : "regexp",\
            "space_controller_name" : "regexp"\
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

        :rtype: LiveActivity or False

        :param search_pattern: dictionary of regexps used for searching through LiveActivity names

        example regexp dict::

            {\
            "live_activity_name" : "GE ViewSync Master on Node A",\
            "space_controller_name" : "ISCtlDispAScreen00"\
            }

        each search_pattern dictionary key may be blank/null
        """
        url = self._compose_url(class_name='Master', method_name='get_live_activities', uri=self.uri)
        self.log.info("Trying to retrieve url=%s" % url)
        response = self._api_get_json(url)
        self.log.debug('Got response for "get_live_activities" %s ' % str(response))
        self.log.info('get_live_activities returned %s objects' % str(len(response)))
        live_activity = self._filter_live_activities(response, search_pattern)

        return self._validate_single_getter_results(live_activity, LiveActivity, LiveActivityNotFoundException)

    def get_live_activity_groups(self, search_pattern=None):
        """
        Retrieves a list of live activity groups.

        :rtype: list

        :param search_pattern: dictionary of regexps used for searching through LiveActivity names

        example regexp dict::

            {\
            "live_activity_group_name" : "regexp"\
            }

        """
        url = self._compose_url(class_name='Master', method_name='get_live_activity_groups', uri=self.uri)
        self.log.info("Trying to retrieve url=%s" % url)
        response = self._api_get_json(url)
        self.log.debug('Got response for "get_live_activity_groups" %s ' % str(response))
        self.log.info('get_live_activity_groups returned %s objects - filtering with %s' % (str(len(response)), search_pattern))
        live_activity_groups = self._filter_live_activity_groups(response, search_pattern)
        return live_activity_groups

    def get_live_activity_group(self, search_pattern=None):
        """
        Retrieves a list of live activity groups.

        :rtype: list

        :param search_pattern: dictionary of regexps used for searching through LiveActivity names

        example regexp dict::

            {\
            "live_activity_group_name" : "regexp"\
            }

        """
        url = self._compose_url(class_name='Master', method_name='get_live_activity_groups', uri=self.uri)
        self.log.info("Trying to retrieve url=%s" % url)
        response = self._api_get_json(url)
        self.log.debug('Got response for "get_live_activity_groups" %s ' % str(response))
        self.log.info('get_live_activity_groups returned %s objects' % str(len(response)))
        live_activity_group = self._filter_live_activity_groups(response, search_pattern)

        return self._validate_single_getter_results(live_activity_group,
                                                    LiveActivityGroup,
                                                    LiveActivityGroupNotFoundException)

    def get_spaces(self, search_pattern=None):
        """
        Retrieves a list of live activity groups.

        :rtype: list

        :param search_pattern: dictionary containing space name regexp

        example regexp dict::

            {"space_name" : "regexp"}

        """
        url = self._compose_url(class_name='Master', method_name='get_spaces', uri=self.uri)
        self.log.info("Trying to retrieve url=%s" % url)
        response = self._api_get_json(url)
        self.log.debug('Got response for "get_spaces" %s ' % str(response))
        spaces = self._filter_spaces(response, search_pattern)
        return spaces

    def get_space(self, search_pattern=None):
        """
        Retrieves a Space

        :rtype: Space

        :param search_pattern: dictionary containing space name regexp

        example regexp dict::

            {"space_name" : "regexp"}

        """
        url = self._compose_url(class_name='Master', method_name='get_spaces', uri=self.uri)
        self.log.info("Trying to retrieve url=%s" % url)
        response = self._api_get_json(url)
        self.log.debug('Got response for "get_spaces" %s ' % str(response))
        space = self._filter_spaces(response, search_pattern)

        return self._validate_single_getter_results(space,
                                                    Space,
                                                    SpaceNotFoundException)

    def get_space_controllers(self, search_pattern=None):
        """
        Retrieves a list of live space controllers.

        :rtype: list

        :param search_pattern: dictionary containing regexps and strings

        example regexp dict::

            {\
            "state" : "STRING",\
            "mode" : "STRING",\
            "name" : "regexp",\
            "uuid" : "STRING"\
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

        :rtype: SpaceController

        :param search_pattern: dictionary containing regexps and strings

        example regexp dict::

            {\
            "space_controller_state" : "STRING",\
            "space_controller_mode" : "STRING",\
            "space_controller_name" : "regexp",\
            "space_controller_uuid" : "STRING"\
            }

        """
        url = self._compose_url(class_name='Master', method_name='get_space_controllers', uri=self.uri)
        self.log.info("Trying to retrieve url=%s" % url)
        response = self._api_get_json(url)
        self.log.debug('Got response for "get_controllers" %s ' % str(response))
        space_controller = self._filter_space_controllers(response, search_pattern)
        return self._validate_single_getter_results(space_controller,
                                                    SpaceController,
                                                    ControllerNotFoundException)

    def get_named_scripts(self, pattern=None):
        """Retrieves a list of named scripts."""
        raise NotImplementedError

    def new_live_activity(self, constructor_args):
        """
        Creates a new live activity and returns it
        :param constructor_args: dictionary containing all of below keys::

            {"live_activity_name": "string containing name of a new live activity (mandatory)",\
            "live_activity_description" : "string containing description",\
            "activity_name" : "string containing activity name",\
            "space_controller_name" : "string containing controller name"}

        :rtype: LiveActivity
        """

        unpacked_arguments={}
        unpacked_arguments['activityId'] = self.get_activity({"activity_name" : constructor_args['activity_name']}).id()
        unpacked_arguments['controllerId'] = self.get_space_controller({"space_controller_name" : constructor_args['space_controller_name']}).id()
        unpacked_arguments['liveActivity.description'] = constructor_args['live_activity_description']
        unpacked_arguments['liveActivity.name'] = constructor_args['live_activity_name']
        unpacked_arguments['_eventId_save'] = 'Save'

        if not self._api_object_exists(LiveActivity, constructor_args, self.get_live_activity):
            activity = LiveActivity().new(self.uri, unpacked_arguments)
            self.log.info("Master:new_live_activity returned activity:%s" % activity)
            return activity
        else:
            return []

    def new_activity(self, constructor_args):
        """
        Creates a new activity and returns it
        :param constructor_args: dictionary containing all of below keys::
            {\
            "zip_file_handler": "zipfile object (mandatory)",\
            "activity_name" : "some name",\
            "activity_version": "some version"\
            }
        :rtype: Activity or False
        """
        if not self._api_object_exists(Activity, constructor_args, self.get_activity):
            activity = Activity().new(self.uri, constructor_args)
            self.log.info("Master:new_activity returned activity:%s" % activity)
            return activity
        else:
            return []

    def new_space_controller(self, constructor_args):
        """
        Creates new controller
        :param constructor_args: dictionary containing all of below keys::
            {\
            "space_controller_name" : "mandatory string",\
            "space_controller_description" : "non mandatory string",\
            "space_controller_host_id" : "mandatory string"\
            }
        """
        if not self._api_object_exists(SpaceController, constructor_args, self.get_space_controller):
            space_controller = SpaceController().new(self.uri, constructor_args)
            self.log.info("Master:new_space_controller:%s" % space_controller)
            return space_controller
        else:
            return []

    def new_live_activity_group(self, constructor_args):
        """
        Creates a new live activity group.
        :param constructor_args: dictionary with following structure::
            {\
            "live_activity_group_name" : "example.py live_activity_group_name",\
            "live_activity_group_description" : "created by example.py",\
            "live_activities" : [{"live_activity_name" : "SV Master on Node A",\
            "space_controller_name" : "ISCtlDispAScreen00"},\
            {"live_activity_name" : "SV Slave 01 on Node A",\
            "space_controller_name" : "ISCtlDispAScreen00"}]\
            }
        """
        self.log.info("Live activities that will comprise new live activity group: %s" % constructor_args['live_activities'])
        live_activity_ids = self._translate_live_activities_names_to_ids(constructor_args['live_activities'])
        unpacked_arguments = {}
        unpacked_arguments['liveActivityGroup.name'] = constructor_args['live_activity_group_name']
        unpacked_arguments['liveActivityGroup.description'] = constructor_args['live_activity_group_description']
        unpacked_arguments['_eventId_save'] = 'Save'
        unpacked_arguments['liveActivityIds'] = live_activity_ids

        if not self._api_object_exists(LiveActivityGroup, constructor_args, self.get_live_activity_group):
            live_activity_group = LiveActivityGroup().new(self.uri, unpacked_arguments)
            self.log.info("Master:new_live_activity_group:%s" % live_activity_group)
            return live_activity_group
        else:
            return []

    def new_space(self, constructor_args):
        """
        Creates a new Space.
        :param constructor_args: dictionary with following structure::
            {\
            "space_name" : "example.py live_activity_group_name",\
            "space_description" : "created by example.py",\
            "live_activity_groups" : [{"live_activity_group_name" : "Media Services"}]\
            }

        """
        live_activity_group_ids = self._translate_live_activity_groups_names_to_ids(constructor_args['live_activity_groups'])
        unpacked_arguments = {}
        unpacked_arguments['space.name'] = constructor_args['space_name']
        unpacked_arguments['space.description'] = constructor_args['space_description']
        unpacked_arguments['_eventId_save'] = 'Save'
        unpacked_arguments['liveActivityGroupIds'] = live_activity_group_ids
        if not self._api_object_exists(Space, constructor_args, self.get_space):
            space = Space().new(self.uri, unpacked_arguments)
            self.log.info("Master:new_space:%s" % space)
            return space
        else:
            return []

    def new_named_script(self, name, description, language, content, scheduled=None):
        """Creates a new named script."""
        raise NotImplementedError

    """ Private methods below """

    def _translate_live_activity_groups_names_to_ids(self, live_activity_groups):
        """
        Converts live activity groups dicts to list of ids

        :param live_activities: list of dictionaries containing following keys::

            {\
            "live_activity_group_name" : "some_name",\
            }

        :rtype: list
        """
        live_activity_groups_ids = []
        for lag_data in live_activity_groups:
            live_activity_group = self.get_live_activity_group(lag_data)
            live_activity_groups_ids.append(live_activity_group.id())
        self.log.info("Translated %s live_activity_groups_names to ids with a result of %s" % (len(live_activity_groups_ids), live_activity_groups_ids) )
        return live_activity_groups_ids

    def _translate_live_activities_names_to_ids(self, live_activities):
        """
        Converts live activities dicts to list of ids

        :param live_activities: list of dictionaries containing following keys::

            {\
            "live_activity_name" : "some_name",\
            "space_controller_name" : "some controller name"\
            }

        :rtype: list
        """
        live_activity_ids = []
        for la_data in live_activities:
            self.log.info("Getting Live Activity for data: %s" % la_data)
            live_activity = self.get_live_activity(la_data)
            live_activity_ids.append(live_activity.id())
        self.log.info("Translated %s live_activity_names to ids with a result of %s" % (len(live_activity_ids), live_activity_ids) )
        return live_activity_ids

    """ Private methods below """

    def _api_object_exists(self, object_type, constructor_args, getter_method):
        self.log.info("Checking whether object %s with following attributes %s exists in the API" % (object_type, constructor_args))

        api_object = getter_method(constructor_args)

        if api_object:
            self.log.warn("Object already exists: %s" % api_object)
            return True
        else:
            self.log.info("Object does not exist yet")
            return False



    def _validate_single_getter_results(self, response, expected_type, exception):
        """
        Validates response from the API. Runs type and other simple checks.

        :param response: list of objects returned from api

        :param expected_type: expected type of the object

        :param exception: exception to throw if response is invalid

        :rtype: interactivespaces object
        """

        if len(response) > 1:
            raise exception("API query returned more than one row")
        elif len(response) == 0:
            return None
        elif isinstance(response[0], expected_type):
            try:
                api_object = response[0].fetch()
                self.log.info("Getter method returned Object:%s" % str(api_object))
                return api_object
            except Exception, e:
                raise
        else:
            raise MasterException("General Master result error for response: %s" % response)

    def _filter_live_activities(self, response, search_pattern):
        """
        Should iterate over response from Master API and filter live activites
        with regard to their name

        :param response: response['data'] from master API

        :param search_pattern: dictionary where values may be regexps

        :todo: refactor filtering because it looks ugly and make it global for all classes
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
            space_controller_name = search_pattern['space_controller_name']
        except Exception:
            space_controller_name = None

        self.log.debug("Filtering activities with pattern=%s" % search_pattern)

        if type(response) == list:
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
        else:
            return []

    def _filter_activities(self, response, search_pattern):
        """
        Should iterate over response from Master API and filter
        live activites with regards to their name

        :param response: response['data'] from master API

        :param search_pattern: dictionary where values may be regexps

        :rtype: list of Activity objects
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

        if type(response) == list:
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
        else:
            return []

    def _filter_live_activity_groups(self, response, search_pattern):
        """
        Should iterate over response from Master API and filter
        live activity groups with regards to their name
        
        :param response: response['data'] from master API
        
        :param search_pattern: dictionary where values may be regexps
        
        :rtype: list of LiveActivityGroup objects
        """
        live_activity_groups = []
        """ Make a search pattern with default values set to None"""
        if isinstance(search_pattern, dict):
            search_pattern = SearchPattern(search_pattern)
        else:
            search_pattern = SearchPattern()
        live_activity_group_name = search_pattern['live_activity_group_name']
        self.log.debug("Filtering activities with pattern=%s" % search_pattern)
        if type(response) == list:
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
        else:
            return []

    def _filter_spaces(self, response, search_pattern):
        """
        Should iterate over response from Master API and filter
        live activity groups with regards to their name
        
        :param response: response['data'] from master API
        
        :param search_pattern: dictionary where values may be regexps
        
        :rtype: list of Space objects
        """
        spaces = []
        """ Make a search pattern with default values set to None"""
        if isinstance(search_pattern, dict):
            search_pattern = SearchPattern(search_pattern)
        else:
            search_pattern = SearchPattern()

        space_name = search_pattern['space_name']

        self.log.debug("Filtering spaces with pattern=%s" % search_pattern)

        if type(response) == list:
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
        else:
            return []

    def _filter_space_controllers(self, response, search_pattern):
        """
        Should iterate over response from Master API and filter
        space controllers with regards to the given search dictionary
        consisting of name, uuid, mode and state (none of them are
        mandatory)
            
        :param response: response['data'] from master API
        
        :param search_pattern: dictionary where values may be regexps
        
        :rtype: list of Space objects

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

        if type(response) == list:
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
        else:
            return []
