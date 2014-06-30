#!/usr/bin/env python
# -*- coding: utf-8 -*-

from exception import PathException
from misc import Logger

class Path(object):
    ''' This class should be responsible for translating (or resolving)
        Master/Activities/Spaces/etc methods into API paths
    '''
    def __init__(self):
        self.routes = {
                       'Master': {
                            'get_activities' : '/activity/all.json',
                            'get_live_activities' : '/liveactivity/all.json',
                            'get_live_activity_groups' : '/liveactivitygroup/all.json',
                            'get_spaces' : '/space/all.json',
                            'get_space_controllers' : '/spacecontroller/all.json',
                            'get_named_scripts' : '/admin/namedscript/all.json',
                            'new_live_activity_group' : '/liveactivitygroup/new',
                            'new_space' : '/space/new.json',
                            'new_controller' : '/spacecontroller/new.json',
                            'new_named_script' : '/admin/namedscript/new.json'
                            },
                       'LiveActivity' : {
                            'status' : '/liveactivity/%s/status.json',
                            'view' : '/liveactivity/%s/view.json',
                            'new' : '/liveactivity/new'
                            },
                       'Activity' : {
                            'view' : '/activity/%s/view.json',
                            'upload' : '/activity/upload'
                            },
                       'LiveActivityGroup' : {
                            'view' : '/liveactivitygroup/%s/view.json',
                            'new' : '/liveactivitygroup/new',
                            'status' : '/liveactivitygroup/status.json'
                            },
                       'Space' : {
                            'view' : '/space/%s/view.json',
                            'status' : '/space/%s/status.json'
                            },
                       'SpaceController' :{
                            'new' : '/spacecontroller/new',
                            'status': '/spacecontroller/%s/status.json'
                            }
                        }
        
        self.log = Logger().get_logger()
        
    def get_route_for(self, class_name, method_name):
        try:
            return self.routes[class_name][method_name]
        except PathException, e:
            self.log.info("Could not return route for class_name %s and method %s because %s" % (class_name, method_name, e))