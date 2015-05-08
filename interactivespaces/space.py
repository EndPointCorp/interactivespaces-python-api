#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mixin import Fetchable, Statusable, Shutdownable, Startupable
from mixin import Deletable, Activatable, Configurable, Metadatable
from mixin import Deployable, Cleanable
from misc import Logger
from serializer import SpaceSerializer
from abstract import Path

class Space(Fetchable, Statusable, Deletable, Shutdownable,
            Startupable, Activatable, Configurable, Metadatable,
            Deployable, Cleanable):
    """
    Space is a LiveActivityGroup container
    """
    def __init__(self, data_hash, uri, name=None, ):
        self.log = Logger().get_logger()
        self.data_hash = data_hash
        self.uri = uri
        self.absolute_url = self._get_absolute_url()
        self.class_name = self.__class__.__name__
        super(Space, self).__init__()
        if (data_hash==None and uri==None):
            self.log.info("No data provided - assuming creation of new Space")
        elif (data_hash!=None and uri!=None):
            self.data_hash = data_hash
            self.uri = uri
            self.absolute_url = self._get_absolute_url()
            self.log.info("Instantiated Space object with url=%s" % self.absolute_url)

    def __repr__(self):
        return str(self.data_hash)

    def __str__(self):
        return self.data_hash

    def new(self, uri, constructor_args):
        """
        Used to create new space through API and set the "uri" so that we
        can operate on this instance of Space right away after .new() returns True

        :param constructor_args: dictionary with following structure::

            {\
            'space.name' : 'space_name',\
            'space.description' : 'space_description',\
            '_eventId_save' : 'Save',\
            'liveActivityGroupIds' : [1,2,666]\
            }

        :param uri: "http://some_server/prefix" (passed by master)

        :rtype: new LiveActivityGroup object or False
        """

        self.log.info("Creating new Space with arguments: %s" % constructor_args)
        route = Path().get_route_for('Space', 'new')
        url = "%s%s" % (uri, route)
        request_response = self._api_post_json(url, constructor_args)
        if request_response.url:
            self.absolute_url = request_response.url.replace("view.html", "view.json")
            self.fetch()
            self.log.info("Created new Space with url=%s, data_hash is now %s" % (self.absolute_url, self.data_hash))
            return self
        else:
            self.log.info("Created new Space %s but returned False" % self)
            return False
        
    def to_json(self):
        """
        Should selected attributes in json form defined by the template
        """
        self.serializer = SpaceSerializer(self.data_hash)
        return self.serializer.to_json()

    def id(self):
        return self.data_hash['id']

    def name(self):
        """
        :param: Should return Space name
        """
        return self.data_hash['name']

    def description(self):
        """
        :param: Should return Space description
        """
        return self.data_hash['description']
    
    def metadata(self):
        """
        :param: Should return Space metadata
        """
        return self.data_hash['metadata']
    
    def live_activity_groups(self):
        """
        :param: Should return Space metadata
        """
        raise NotImplemented

    """ Private methods below """

    def _get_absolute_url(self):
        live_activity_group_id = self.data_hash['id']
        url = "%s/space/%s/view.json" % (self.uri, live_activity_group_id)
        return url
