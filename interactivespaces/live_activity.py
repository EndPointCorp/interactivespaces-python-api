#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mixin import Fetchable, Statusable, Shutdownable, Startupable
from mixin import Deletable, Activatable, Configurable, Cleanable
from mixin import Metadatable, Deployable
from exception import LiveActivityException
from serializer import LiveActivitySerializer
from misc import Logger
from abstract import Path

class LiveActivity(Fetchable, Statusable, Deletable, Shutdownable,
                   Startupable, Activatable, Configurable, Cleanable,
                   Metadatable, Deployable):
    """
        @summary: Should be responsible for managing single LiveActivity
        @todo: .new() should return instance of fetched live activity
    """
    def __init__(self, data_hash=None, uri=None):
        """
            @summary: when called with constructor_args and other vars set to None, new
            LiveActivity will be created
            @param data_hash: should be master API liveActivity json, may be blank
            @param uri: should be a link to "view.json" of the given live activity
        """
        self.log = Logger().get_logger()
        self.class_name = self.__class__.__name__
        super(LiveActivity, self).__init__()
        if (data_hash==None and uri==None):
            self.log.info("No data provided - assuming creation of new LiveActivity")
        elif (data_hash!=None and uri!=None):
            self.data_hash = data_hash
            self.uri = uri
            self.absolute_url = self._get_absolute_url()
            self.log.info("Instantiated LiveActivity object with url=%s" % self.absolute_url)

    def __repr__(self):
        return str(self.data_hash)

    def new(self, uri, new_data_hash):
        """
        @summary: used to create new live activity through API and set the "uri" so that we
            can operate on this instance of LiveActivity right away after .new() returns True
        @param new_data_hash: dict {"live_activity_name" : "",
                                        "live_activity_description" : "",
                                        "activity_id" : "",
                                        "controller_id" : ""
                                        }
        @param uri: "http://some_server/prefix (passed by master)"
        @rtype: new LiveActivity object or False
        """
        self.log.info("Creating new Live Activity with arguments: %s" % new_data_hash)
        route = Path().get_route_for('LiveActivity', 'new')
        url = "%s%s" % (uri, route)
        request_response = self._api_post_json(url, new_data_hash)
        if request_response.url:
            self.absolute_url = request_response.url.replace("view.html", "view.json")
            self.fetch()
            self.log.info("Created new LiveActivity with url=%s, data_hash is now %s" % (self.absolute_url, self.data_hash))
            return self
        else:
            self.log.info("Created new LiveActivity %s but returned False" % self)
            return False

    def to_json(self):
        """
            @summary: Should selected attributes in json form defined by the template
        """
        self.serializer = LiveActivitySerializer(self.data_hash)
        return self.serializer.to_json()

    def name(self):
        """
            @summary: Should return live activity name
        """
        return self.data_hash['name']

    def status(self):
        """
            @summary: Should return status that is currently held in the object instance
        """
        try:
            status_data = self.data_hash['active']['runtimeState']
            return status_data
        except LiveActivityException("Activity not running or non existent"):
            return "UNKNOWN"

    def identifying_name(self):
        """
            @summary: Should return LiveActivity identifying name
        """
        return self.data_hash['activity']['identifyingName']

    def version(self):
        """
            @summary: Should return LiveActivity version
        """
        return self.data_hash['activity']['version']

    def metadata(self):
        """
            @summary: Should return LiveActivity metadata
        """
        return self.data_hash['metadata']

    def id(self):
        """
            @summary: Should return LiveActivity id
            @rtype: string
        """
        return self.data_hash['id']

    """ Private methods below this text """

    def _get_absolute_url(self):
        """
        @rtype: string
        """
        route = Path().get_route_for(self.class_name, 'view') % self.data_hash['id']
        url = "%s%s" % (self.uri, route)
        return url
