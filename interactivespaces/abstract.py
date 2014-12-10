#!/usr/bin/env python
# -*- coding: utf-8 -*-

from exception import PathException
from misc import Logger
import requests
import urllib2
import urlparse
import json
import os
import websocket
import re
from timeout_wrapper import time_limit


class TimeoutException(Exception):
    pass


class APICallException(Exception):
    pass


class APICall:
    def __init__(self, url):
        self.url = url
        self.log = Logger().get_logger()

    def __repr__(self):
        return str("APICall to %s" % self.url)

    def get_url(self):
        raise Exception("Instantiate some APICall subclass; don't call it directly")

    def set_uri(self,uri):
        self.uri = uri

    def can_call(self):
        try:
            if not self.uri:
                raise APICallException("URI must be set (use set_uri() method) before calling this APICall object")
        except AttributeError, e:
            raise APICallException("URI must be set (use set_uri() method) before calling this APICall object")
        return True

    def call(self, params=None, file_handler=False, cookies=False, extra_data={}):
        self._call(params, file_handler, cookies, extra_data)

    def parameterize(self, params):
        # Poor man's abstract class
        raise Exception("Instantiate some APICall subclass; don't call it directly.")

    def get_url(self):
        return "%s%s" % (self.uri, self.url)

class RESTCall(APICall):
    def parameterize(self, params):
        if self.url.find("%s"):
            self.url = self.url % params

    def get_url(self):
        return "%s%s" % (self.uri["http"], self.url)

    def _call(self, params=None, file_handler=False, cookies=False, extra_data={}):
        if not self.can_call():
            return

        if file_handler:
            head, tail = os.path.split(file_handler.name)
            file_name = tail
            file_content_type = "application/zip"
            files = {"activityFile" : (file_name , file_handler, file_content_type)}
        else:
            files = None

        self.log.info("Trying url %s" % self.get_url())

        if cookies == False and params == None:
            response = urllib2.urlopen(self.get_url())
            response_str = response.read()

            try:
                data = json.loads(response_str)
                out_data = data['data']
                if data['result'] != 'success':
                    self.log.info("Could not retrieve data for URL=%s" % url)
                    return False
            except Exception:
                out_data = None

            return out_data
        else:
            session = requests.session()
            get_response = session.get(self.get_url())
            query = urlparse.urlparse(get_response.url).query
            cookies = {"JSESSIONID" : session.cookies['JSESSIONID']}
            url = self.get_url() + "?" + query
            post_response = session.post(url=url, cookies=cookies, data=params, files=files) 
            if post_response.status_code == 200:
                self.log.info("_api_post_json returned 200 with post_response.url=%s" % post_response.url)
                return post_response
            else:
                self.log.info("_api_post_json returned post_response.status_code %s" % post_response.status_code)
                return False

class WebSocketCall(APICall):
    requestId = 0

    def parameterize(self, params):
        self.id = params

    def get_url(self):
        return self.uri["ws"]

    def getCommandJson(self, extra_data):
        # {"type":"/liveactivity/all","requestId":"1","data":{"filter":"name.equals('LG Browser Service')"}}
        WebSocketCall.requestId += 1
        obj = {
            "type": self.url,
            "requestId": str(WebSocketCall.requestId),
            "data": extra_data
        }
        try:
            obj['data']['id'] = self.id
        except:
            # Don't complain if I haven't parameterized this
            pass
        return json.dumps(obj)

    def _call(self, params=None, file_handler=None, cookies=None, extra_data={}):
        if not self.can_call():
            return

        iterations = 0

        while iterations < 10:
            iterations += 1
            ws = websocket.create_connection(self.get_url())
            c = self.getCommandJson(extra_data)
            ws.send(c)
            print "Sent data %s" % c
            try:
                with time_limit(5):
                    result = ws.recv()
            except TimeoutException, msg:
                print "Timed out! %s" % msg
            print "received response %s" % result
            try:
                data = json.loads(result)
                out_data = None

                if data['result'] != 'success':
                    self.log.info("Could not retrieve data for URL=%s" % url)
                    return False

                try:
                    out_data = data['data']
                except Exception as e:
                    pass

            except Exception as e:
                print "Exception: %s" % e
                out_data = None
                print "Trying again"
                continue

            return out_data


class Path(object):
    '''
    Should be responsible for static translation of routes
    '''
    def __init__(self):
        self.routes = {
                       'Master': {
                            'get_activities' : '/activity/all.json',
                            #'get_live_activities' : '/liveactivity/all.json',
                                # XXX Pass a handler in cases where I don't want the commandresponse packet from teh websocket API
                            'get_live_activities' : WebSocketCall('/liveactivity/all'),
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
                            #'status' : '/liveactivity/%s/status.json',
                            'status' : WebSocketCall('/liveactivity/status'),
                            'view' : '/liveactivity/%s/view.json',
                            'new' : '/liveactivity/new',
                            'delete' : '/liveactivity/%s/delete.html',
                            'shutdown' : '/liveactivity/%s/shutdown.json',
                            'startup' : '/liveactivity/%s/startup.json',
                            'activate' : '/liveactivity/%s/activate.json',
                            'deactivate' : '/liveactivity/%s/deactivate.json',
                            'deploy' : '/liveactivity/%s/deploy.json',
                            'configure' : WebSocketCall('/liveactivity/configure'),
                            'set_config' : WebSocketCall('/liveactivity/configuration/set'),
                            'clean_tmp' : '/liveactivity/%s/cleantmpdata.json',
                            'clean_permanent' : '/liveactivity/%s/cleanpermanentdata.json',
                            'metadata' : '/liveactivity/%s/metadata/edit'
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
                            'new' : '/space/new',
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
                            'view' : '/spacecontroller/%s/view.json',
                            'status': '/spacecontroller/%s/status.json',
                            'delete': '/spacecontroller/%s/delete.html',
                            'shutdown': '/spacecontroller/%s/shutdown.json',
                            'deploy': '/spacecontroller/%s/deploy.json',
                            'connect' : '/spacecontroller/%s/connect.json',
                            'disconnect' : '/spacecontroller/%s/disconnect.json'
                            }
                        }

        self.log = Logger().get_logger()

    def get_route_for(self, class_name, method_name, param=None):
        """
        Should receive caller class name and caller method in order
        to return a proper route in the master API

        :rtype: string
        """
        try:
            r = self.routes[class_name][method_name]
            if not isinstance(r, APICall):
                # Default to RESTCall, not WebSocketCall
                r = RESTCall(r)

            if param != None:
                r.parameterize(param)

            return r
        except PathException, e:
            self.log.info("Could not return route for class_name %s and method %s because %s" % (class_name, method_name, e))
