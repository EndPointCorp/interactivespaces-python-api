#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mixin import Fetchable, Statusable, Shutdownable, Startupable
from mixin import Deletable, Activatable, Configurable, Metadatable
from mixin import Deployable, Cleanable
from misc import Logger
from serializer import SpaceSerializer

class Space(Fetchable, Statusable, Deletable, Shutdownable,
            Startupable, Activatable, Configurable, Metadatable,
            Deployable, Cleanable):
    """
    Space is a LiveActivityGroup aggregator
    """
    def __init__(self, data_hash, uri, name=None, ):
        self.log = Logger().get_logger()
        self.data_hash = data_hash
        self.uri = uri
        self.absolute_url = self._get_absolute_url()
        self.class_name = self.__class__.__name__
        super(Space, self).__init__()
        self.log.info("Instantiated Activity object with url=%s" % self.absolute_url)

    def __repr__(self):
        return str(self.data_hash)

    def __str__(self):
        return self.data_hash

    def create(self, live_activity_group_name, live_activity_names):
        """
        Should be responsible for creating space
            
        :param live_activity_group_name: string
            
        :param live_activity_names: list of existing names
        """
        raise NotImplementedError

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
        :param: Should return live activity name
        """
        return self.data_hash['name']

    def description(self):
        """
        :param: Should return Space description
        """
        return self.data_hash['description']

    """ Private methods below """

    def _get_absolute_url(self):
        live_activity_group_id = self.data_hash['id']
        url = "%s/space/%s/view.json" % (self.uri, live_activity_group_id)
        return url
