#!/usr/bin/env python
# -*- coding: utf-8 -*-

from exception import PathException
from misc import Logger

class Path(object):
    '''
    Should be responsible for static translation of routes
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
                       'Activity' : {
                            'view' : '/activity/%s/view.json',
                            'upload' : '/activity/upload',
                            'delete' : '/activity/%s/delete.html'
                            },
                       'LiveActivity' : {
                            'status' : '/liveactivity/%s/status.json',
                            'view' : '/liveactivity/%s/view.json',
                            'new' : '/liveactivity/new',
                            'delete' : '/liveactivity/%s/delete.html',
                            'shutdown' : '/liveactivity/%s/shutdown.json',
                            'startup' : '/liveactivity/%s/startup.json',
                            'activate' : '/liveactivity/%s/activate.json',
                            'deactivate' : '/liveactivity/%s/deactivate.json',
                            'deploy' : '/liveactivity/%s/deploy.json',
                            'configure' : '/liveactivity/%s/configure.json',
                            'clean_tmp' : '/liveactivity/%s/cleantmpdata.json',
                            'clean_permanent' : '/liveactivity/%s/cleanpermanentdata.json',
                            'metadata' : '/liveactivity/%s/metadata/edit'
                            'config' : '/liveactivity/%s/config/edit'
                            },
                       'LiveActivityGroup' : {
                            'view' : '/liveactivitygroup/%s/view.json',
                            'new' : '/liveactivitygroup/new',
                            'status' : '/liveactivitygroup/%s/liveactivitystatus.json',
                            'delete' : '/liveactivitygroup/%s/delete.html',
                            'shutdown' : '/liveactivitygroup/%s/shutdown.json',
                            'startup' : '/liveactivitygroup/%s/startup.json',
                            'activate' : '/liveactivitygroup/%s/activate.json',
                            'deactivate' : '/liveactivitygroup/%s/deactivate.json',
                            'deploy' : '/liveactivitygroup/%s/deploy.json',
                            'configure' : '/liveactivitygroup/%s/configure.json',
                            'metadata' : '/liveactivitygroup/%s/metadata/edit',
                            'edit' : '/liveactivitygroup/%s/edit.json'
                            },
                       'Space' : {
                            'view' : '/space/%s/view.json',
                            'status' : '/space/%s/status.json',
                            'delete' : '/space/%s/delete.html',
                            'shutdown' : '/space/%s/shutdown.json',
                            'startup' : '/space/%s/startup.json',
                            'activate' : '/space/%s/activate.json',
                            'deactivate' : '/space/%s/deactivate.json',
                            'deploy' : '/space/%s/deploy.json',
                            'configure' : '/space/%s/configure.json',
                            'metadata' : '/space/%s/metadata/edit'
                            },
                       'SpaceController' :{
                            'new' : '/spacecontroller/new',
                            'status': '/spacecontroller/%s/status.json',
                            'delete': '/spacecontroller/%s/delete.html',
                            'shutdown': '/spacecontroller/%s/shutdown.json',
                            'deploy': '/spacecontroller/%s/deploy.json',
                            'connect' : '/spacecontroller/%s/connect.json',
                            'disconnect' : '/spacecontroller/%s/disconnect.json'
                            }
                        }

        self.log = Logger().get_logger()

    def get_route_for(self, class_name, method_name):
        """
        Should receive caller class name and caller method in order
        to return a proper route in the master API
            
        :rtype: string
        """
        try:
            return self.routes[class_name][method_name]
        except PathException, e:
            self.log.info("Could not return route for class_name %s and method %s because %s" % (class_name, method_name, e))
