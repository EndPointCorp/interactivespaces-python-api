#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mixin import Statusable, Fetchable
from exception import LiveActivityException
from serializer import LiveActivitySerializer
from misc import Logger
from abstract import Path

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

or:

data: {
lastDeployDate: "Mon May 05 12:50:36 PDT 2014",
outOfDate: false,
id: "110",
description: "",
name: "Evdev Demuxer on 42-a",
active: {
numberLiveActivityGroupRunning: 1,
runtimeState: "RUNNING",
deployState: "UNKNOWN",
lastStateUpdate: "Fri Jun 06 07:13:25 PDT 2014",
runtimeStateDescription: "space.activity.state.running",
directRunning: false,
directActivated: false,
numberLiveActivityGroupActivated: 0,
deployStateDescription: "space.activity.state.unknown",
deployStateDetail: null,
runtimeStateDetail: "<table class="status-detail"><tr class="activity-status"><td>Activity Status</td><td>RUNNING</td></tr> <tr class="component-status"><td>Message Router</td><td><table class="route-detail"><tr class="node-name"><td>Node Name</td><td>:</td><td>/ctldispascreen00/liquidgalaxy/evdev/demuxer/default</td></tr> <tr class="output-route"><td>abs</td><td>&#8594;</td><td>/liquidgalaxy/generic/evdev/default/abs</td></tr> <tr class="output-route"><td>key</td><td>&#8594;</td><td>/liquidgalaxy/generic/evdev/default/key</td></tr> <tr class="input-route"><td>raw</td><td>&#8592;</td><td>/liquidgalaxy/generic/evdev/default/raw</td></tr> <tr class="output-route"><td>rel</td><td>&#8594;</td><td>/liquidgalaxy/generic/evdev/default/rel</td></tr> </table></td></tr> <tr class="managed-resources"><td>Managed Resources</td><td></td></tr> </table>"
},
controller: {
id: "2",
name: "ISCtlDispAScreen00",
uuid: "372f0f95-6b48-487a-a1ac-383ba580fc1c"
},
uuid: "88816d20-22f6-4f78-95ba-7843696c6bc5",
activity: {
id: "61",
bundleContentHash: "98b5cf0d8f68642fcc1eb0d66622323e7692c78e615252a9ac414450bd0a7743655f7648c38d1bfbcb0907408376bd0e1db519cb51cb78fe39191070b6293592",
identifyingName: "com.endpoint.lg.evdev.demuxer",
lastUploadDate: 1398288062862,
description: "Separates and aggregates different types of input events.",
name: "Event Device Demuxer",
lastStartDate: 1402064004937,
metadata: { },
version: "1.0.0.dev"
},
metadata: { }
}
}
 
"""

class LiveActivity(Statusable, Fetchable):
    def __init__(self, data_hash, uri):
        self.data_hash = data_hash
        self.uri = uri
        self.log = Logger().get_logger()
        ''' Add all mixins for thingies like api communication, status retrieval etc'''
        super(LiveActivity, self).__init__()
        self.absolute_url = self.get_absolute_url()
        self.log.info("Instantiated LiveActivity object with url=%s" % self.absolute_url)
        
    def get_absolute_url(self):
        activity_id = self.data_hash['id']
        url = "%s/liveactivity/%s/view.json" % (self.uri, activity_id)
        return url  
    
    def send_status_refresh(self):
        """ 
            Should use Statusable._send_status_refresh to make Master ask Controller for the
            status of LiveActivity. After that it's good to refresh the object"
        """
        refresh_route = Path().get_route_for('LiveActivity', 'status') % self.data_hash['id']
        if self._send_status_refresh_command(refresh_route):
            self.log("Successfully refreshed status for LiveActivity url=%s" % self.absolute_url) 
            return True
        else:
            return False
    
    def fetch(self):
        """ 
            Should retrieve private data for an object from Master API
        """
        self.data_hash = self._refresh_object(self.absolute_url)
    
    def to_json(self):
        """ Should selected attributes in json form defined by the template"""
        self.serializer = LiveActivitySerializer(self.data_hash)
        return self.serializer.to_json()
    
    def name(self):
        """ Should return live activity name"""
        return self.data_hash['name']
    
    def status(self):
        """ Should return status that is currently held in the object instance"""
        try:
            status_data = self.data_hash['active']['runtimeState']
            return status_data
        except LiveActivityException("Activity not running or non existent"):
            return "UNKNOWN"
 
    def identifying_name(self):
        """ Should return LiveActivity identifying name """
        return self.data_hash['activity']['identifyingName']
    
    def version(self):
        """ Should return LiveActivity version """
        return self.data_hash['activity']['version']
    
    def id(self):
        """ Should return LiveActivity id """
        return self.data_hash['activity']['id']
        
        
    
    
    
        
