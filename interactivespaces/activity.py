#!/usr/bin/env python
# -*- coding: utf-8 -*-

from exception import ActivityException
from misc import Logger
from mixin import Fetchable
from serializer import ActivitySerializer

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

class Activity(Fetchable):
    """ Should be responsible for setting an getting attributes of an activity """
    def __init__(self, data_hash, uri, activity_archive_uri=None, name=None):
        self.log = Logger().get_logger()
        if ((not data_hash) and (not uri)) and (activity_archive_uri and name):            
            self.log.info("Deploying new activity from %s" % activity_archive_uri)
            self.deploy()
        else:
            self.data_hash = data_hash
            self.uri = uri
            ''' Add all mixins for thingies like api communication, status retrieval etc'''
            self.absolute_url = self.get_absolute_url()
            self.log.info("Instantiated Activity object with url=%s" % self.absolute_url)

        super(Activity, self).__init__()
    
    def deploy(self):
        """ 
            Should make a deployment of the activity with followin steps:
            - download/unpack the activity from an activity_archive_uri
            - upload it to the API  
            - save
            - set instance variables for the object
            """
        pass
    
        
    def to_json(self):
        """ 
            Should selected attributes in json form defined by the template
        """
        self.serializer = ActivitySerializer(self.data_hash)
        return self.serializer.to_json()
    
    def get_absolute_url(self):
        activity_id = self.data_hash['id']
        url = "%s/activity/%s/view.json" % (self.uri, activity_id)
        return url  
    
    def fetch(self):
        """ Should retrieve data from Master API"""
        self.data_hash = self._refresh_object(self.absolute_url)
    
    def name(self):
        """ Should return live activity name"""
        return self.data_hash['activity']['name']  
    
    def identifying_name(self):
        """ Should return identifying name """
        return self.data_hash['activity']['identifyingName']
    
    def version(self):
        """ Should return Activity version """
        return self.data_hash['activity']['version']
    
    def id(self):
        """ Should return Activity id """
        return self.data_hash['activity']['id']
  
    def description(self):
        """ Should return Activity description """
        return self.data_hash['activity']['description']
    
    
        
