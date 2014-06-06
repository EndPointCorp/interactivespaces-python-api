#!/usr/bin/env python
# -*- coding: utf-8 -*-

from exception import PathException
from misc import PathLogger

class Path(object):
    ''' This class should be responsible for translating (or resolving)
        Master/Activities/Spaces/etc methods into API paths
    '''
    def __init__(self):
        self.routes = {
                       'Master': {
                            'get_activities' : '/activity/all.json',
                            'get_live_activities' : '/liveactivity/all.json',
                            'get_live_activity_groups' : '',
                            'get_spaces' : '',
                            'get_controllers' : '',
                            'get_named_scripts' : '',
                            'new_live_activity' : '',
                            'new_live_activity_group' : '',
                            'new_space' : '',
                            'new_controller' : '',
                            'new_named_script' : ''
                            },
                       'LiveActivity' : {
                            'status' : 'asdf'
                            }
                        }
        self.log = PathLogger().get_logger()
        
    def get_route_for(self, class_name, method_name):
        try:
            return self.routes[class_name][method_name]
        except PathException, e:
            self.log.info("Could not return route for context %s and method %s because %s" % (class_name, method_name, e))
        
        
