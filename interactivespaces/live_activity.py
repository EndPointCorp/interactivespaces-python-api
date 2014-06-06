#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mixin import Statusable

"""
Reminder for Json data representing an activity:
{u'data': [{u'activity': {u'identifyingName': u'com.endpoint.lg.earth.webui',
    u'metadata': {},
    u'version': u'1.0.0.dev'},
   u'controller': {u'id': u'1',
    u'name': u'lg2-1',
    u'uuid': u'ded53fca-9e40-4e3e-a71f-3b65f071b241'},
   u'deployStatus': u'space.activity.state.unknown',
   u'description': u'pokpok',
   u'id': u'101',
   u'metadata': {},
   u'name': u'pokpok',
   u'status': u'space.activity.state.unknown',
   u'uuid': u'e9215bb6-5b60-42fa-b369-d23e44650fff'}],
 u'result': u'success'}
 
"""

class LiveActivity(Statusable):
    def __init__(self, data_object, absolute_url):
        self.data_object = data_object
        self.absolute_url
        ''' Add all mixins for thingies like api communication, status retrieval etc'''
        super(LiveActivity, self).__init__()
        
    def unpack_attributes(self):
        """ Unpack all json attributes to instance vars """
        pass
