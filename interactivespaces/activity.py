#!/usr/bin/env python
# -*- coding: utf-8 -*-

from exception import ActivityException
from misc import Logger
from mixin import Refreshable

"""
data: {
liveactivities: [
{
lastDeployDate: "Mon May 05 12:50:37 PDT 2014",
outOfDate: false,
id: "111",
description: "",
name: "LG UI Browser on 42-a",
active: {
numberLiveActivityGroupRunning: 1,
runtimeState: "ACTIVE",
deployState: "UNKNOWN",
lastStateUpdate: "Fri Jun 06 09:55:47 PDT 2014",
runtimeStateDescription: "space.activity.state.active",
directRunning: true,
directActivated: true,
numberLiveActivityGroupActivated: 0,
deployStateDescription: "space.activity.state.unknown",
deployStateDetail: null,
runtimeStateDetail: ""
},
controller: {
id: "2",
name: "ISCtlDispAScreen00",
uuid: "372f0f95-6b48-487a-a1ac-383ba580fc1c"
},
uuid: "f3ead998-9e85-4185-bf51-c3970c61ff28",
activity: {
id: "53",
bundleContentHash: "13aded35407d4bb000ddde019d1a675fce85f6bcd7909cc421b47caa11306522bbee7bf363732fd260427c3fbd457d83ee8e618f8a1fed938a31db8f3f62eb0c",
identifyingName: "com.endpoint.lg.browser",
lastUploadDate: 1398288057444,
description: "Browser Activity to present "webui" activties to the user",
name: "Browser Activity",
lastStartDate: 1402064020012,
metadata: { },
version: "1.0.0.dev"
},
metadata: { }
}
],
activity: {
id: "53",
bundleContentHash: "13aded35407d4bb000ddde019d1a675fce85f6bcd7909cc421b47caa11306522bbee7bf363732fd260427c3fbd457d83ee8e618f8a1fed938a31db8f3f62eb0c",
identifyingName: "com.endpoint.lg.browser",
dependencies: [ ],
lastUploadDate: 1398288057444,
description: "Browser Activity to present "webui" activties to the user",
name: "Browser Activity",
lastStartDate: 1402064020012,
metadata: { },
version: "1.0.0.dev"
}
}
}
"""

class Activity(Refreshable):
    def __init__(self, data_hash, uri):
        self.data_hash = data_hash
        self.uri = uri
        self.log = Logger().get_logger()
        ''' Add all mixins for thingies like api communication, status retrieval etc'''
        self.absolute_url = self.get_absolute_url()
        self.log.info("Instantiated Activity object with url=%s" % self.absolute_url)
        super(Activity, self).__init__()
                
    def get_absolute_url(self):
        activity_id = self.data_hash['id']
        url = "%s/activity/%s/view.json" % (self.uri, activity_id)
        return url  
    
    def refresh(self):
        self.data_hash = self.refresh_object()
    
    def name(self):
        """ Should return live activity name"""
        return self.data_hash['name']
    
        
        
    
    
    
        
