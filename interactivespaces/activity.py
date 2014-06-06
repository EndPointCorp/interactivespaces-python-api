#!/usr/bin/env python
# -*- coding: utf-8 -*-

from exception import ActivityException
from misc import Logger
from mixin import Refreshable

"""
{
result: "success",
data: [
[...]
{
id: "59",
bundleContentHash: "4b186c487177389ad6e9b8ef7c8b854db469a482e0228730b2eb598fb0dbc1fe70f41d40cddd17a8c5b212434264d54ae7806b5b80e4b251cb6a327b3b2a057f",
identifyingName: "com.endpoint.lg.streetview.pano",
lastUploadDate: 1398288061464,
description: "Runs Google Street View.",
name: "Street View Panorama",
lastStartDate: 1402064006465,
metadata: { },
version: "1.0.0.dev"
},
{
id: "57",
bundleContentHash: "9a4392d9457ce31c96ef2bb082eacedd914b65f1a7a7616e8bdbaae395dcef4a0c1f0045aaed13afa7f7b79048babc509d432b4a7600388850ff32c8ac83babb",
identifyingName: "com.endpoint.lg.webctl",
lastUploadDate: 1398288062678,
description: "Serves a web interface for the Liquid Galaxy.",
name: "Web Control",
lastStartDate: 1402063997800,
metadata: { },
version: "1.0.0.dev"
}
]
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
        """ Should retrieve data from Master API"""
        self.data_hash = self._refresh_object(self.absolute_url)
    
    """ Public attributes below """
    
    def name(self):
        """ Should return live activity name"""
        return self.data_hash['activity']['name']  
    
    def identifying_name(self):
        """ Should return identifying name """
        return self.data_hash['activity']['identifyingName']
    
    def version(self):
        """ Should return Activity version """
        return self.data_hash['activity']['version']
    
    def activity_id(self):
        """ Should return Activity id """
        return self.data_hash['activity']['id']
    
    
    
        
