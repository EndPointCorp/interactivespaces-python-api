#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mixin import Communicable
from exception import MasterException
from abstract import Path

class Master(Communicable):
    def __init__(self, host='lg-head', prefix='/interactivespaces', port=8080):
        ''' 
            Instantiate the Master class with host and port only.
            Communication layer and route logic should be inherited from somewhere else
        '''
      
        self.host = host
        self.prefix = prefix
        self.port = port
        self.paths = Path()
        '''Add communication layer to master'''
        super(Master, self).__init__() 

    def get_activities(self, pattern=None):
        """Retrieves a list of activities."""
    
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