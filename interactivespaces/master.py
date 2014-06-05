#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2

class MasterException(Exception):
  pass

class Master(object):
  def __init__(self, host, port):
    self.host = host
    self.port = port

  def _urlopen(self, url, data=None):
    """Helper for opening urls."""
    return urllib2.urlopen(url, data)

  def _api_get_json(self, command):
    """Sends a request to the master, returns the response data."""
    raise NotImplementedError

  def _api_get_html(self, command, query=None):
    """Sends a request to the master, returns the response."""
    raise NotImplementedError

  def _api_post_json(self, command, query=None, data=None):
    """Sends data to the master."""
    raise NotImplementedError

  def _api_post_html(self, command, query=None, data=None):
    """Sends data to the master."""
    raise NotImplementedError

  def get_activities(self, pattern=None):
    """Retrieves a list of activities."""
    raise NotImplementedError

  def get_live_activities(self, pattern=None):
    """Retrieves a list of live activities."""
    raise NotImplementedError

  def get_live_activity_groups(self, pattern=None):
    """Retrieves a list of live activity groups."""
    raise NotImplementedError

  def get_spaces(self, pattern=None):
    """Retrieves a list of spaces."""
    raise NotImplementedError

  def get_controllers(self, pattern=None):
    """Retrieves a list of controllers."""
    raise NotImplementedError

  def get_named_scripts(self, pattern=None):
    """Retrieves a list of named scripts."""
    raise NotImplementedError

  def new_live_activity(self, name, description, activity, controller):
    """Creates a new live activity."""
    raise NotImplementedError

  def new_live_activity_group(self, name, description, live_activities):
    """Creates a new live activity group."""
    raise NotImplementedError

  def new_space(self, name, description, live_activity_groups, spaces):
    """Creates a new space."""
    raise NotImplementedError

  def new_controller(self, name, description, host_id):
    """Creates a new controller."""
    raise NotImplementedError

  def new_named_script(self, name, description, language, content, scheduled=None):
    """Creates a new named script."""
    raise NotImplementedError
