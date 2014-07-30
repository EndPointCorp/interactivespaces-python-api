#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append("../")
sys.path.append("/home/galadmin/src/interactivespaces-python-api/")
from interactivespaces import Master
import ConfigParser
from optparse import OptionParser
import pprint
import time
from subprocess import call, PIPE, Popen
from interactivespaces.exception import ControllerNotFoundException

'''
TODO: 
- refactor connect_all_controllers()
- manage sys.path in the appropriate way without hardcoded paths and .append()
- make config file steer the debug level for the @debug decorator
'''

__report_indent = [0]

def debug(fn):
    def wrap(*params, **kwargs):
        call = wrap.callcount = wrap.callcount + 1

        indent = ' ' * __report_indent[0]
        fc = "%s(%s)" % (fn.__name__, ', '.join(
            [a.__repr__() for a in params] + 
            ["%s = %s" % (a, repr(b)) for a, b in kwargs.items()]
        ))

        print("%s%s called [#%s]" % (indent, fc, call))
        __report_indent[0] += 1
        ret = fn(*params, **kwargs)
        __report_indent[0] -= 1
        print("%s%s returned %s [#%s]" % (indent, fc, repr(ret), call))
        return ret
    wrap.callcount = 0
    return wrap


class InteractiveSpacesRelaunch(object):
    @debug
    def __init__(self, config_path):
        self.config_path = config_path
        self.init_config()
        self.master = Master(host=self.host, port=self.port, logfile_path=self.log_path)
        self.relaunch_container = []
        self.stopped = False
        self.activated = False

    @debug
    def init_config(self):
        self.config = ConfigParser.RawConfigParser()
        self.config.read(self.config_path)
        self.host = self.config.get('master', 'host')
        self.port = self.config.get('master', 'port')
        self.shutdown_attempts = self.config.getint('relaunch', 'shutdown_attempts')
        self.startup_attempts = self.config.getint('relaunch', 'startup_attempts')
        self.relaunch_sequence = self.config.get('relaunch', 'relaunch_sequence').split(',')
        self.interval_between_attempts = self.config.getint('relaunch', 'interval_between_attempts')
        self.relaunch_controllers = self.config.getint('relaunch', 'relaunch_controllers')
        self.relaunch_master = self.config.getint('relaunch', 'relaunch_master')
        self.log_path = self.config.get('global', 'logfile_path')
        self.ssh_command = self.config.get('global', 'ssh_command')
        self.pp = pprint.PrettyPrinter(indent=4)
        self.controllers_data = self.init_controllers_config()
        
        
    @debug
    def init_controllers_config(self):
        config = {}
        controllers_list = self.config.get('global', 'controllers_list').split(',')
        for controller_name in controllers_list:
            config[controller_name] = {}
            config[controller_name]['name'] = self.config.get(controller_name, 'name')
            config[controller_name]['hostname'] = self.config.get(controller_name, 'hostname')
            config[controller_name]['stop_command'] = self.config.get(controller_name, 'stop_command')
            config[controller_name]['launch_command'] = self.config.get(controller_name, 'launch_command')
            config[controller_name]['pid_command'] = self.config.get(controller_name, 'pid_command')
            config[controller_name]['destroy_tmux_command'] = self.config.get(controller_name, 'destroy_tmux_command')
        return config
    
    @debug 
    def controller_connected(self, controller_name):
        """
        @summary: We always return False because ispaces controllers are tricky
        """
        try:
            controller = self.master.get_space_controller({'space_controller_name' : controller_name,
                                                           'space_controller_mode' : 'ENABLED',
                                                           'space_controller_state': 'RUNNING'})
            return True
        except ControllerNotFoundException, e :
            print "Controller '%s' not connected" % controller_name
            return False
    
    @debug
    def stop_controller(self, controller_name):
        command = "%s %s '%s'" % (self.ssh_command, controller_name, self.controllers_data[controller_name]['stop_command'])
        print command
        cmd_process = Popen(command, shell=True, stdout=PIPE)
        output = cmd_process.communicate()[0].replace('\n', '').split(' ')
        print output
        return output
    
    @debug 
    def destroy_tmux_session(self, controller_name):
        command = "%s %s '%s'" % (self.ssh_command, controller_name, self.controllers_data[controller_name]['destroy_tmux_command'])
        print command
        cmd_process = Popen(command, shell=True, stdout=PIPE)
        output = cmd_process.communicate()[0].replace('\n', '').split(' ')
        print output
        return output
        
    @debug
    def start_controller(self, controller_name):
        command = "%s %s '%s'" % (self.ssh_command, controller_name, self.controllers_data[controller_name]['launch_command'])
        print command
        cmd_process = Popen(command, shell=True, stdout=PIPE)
        output = cmd_process.communicate()[0].replace('\n', '').split(' ')
        print output
        return output
    
    @debug
    def connect_controller(self, controller_name):
        controller = self.master.get_space_controller({'space_controller_name' : controller_name})
        controller.send_connect()
        self.wait(3)
        controller.send_status_refresh()
        pass
    
    @debug
    def connect_all_controllers(self):
        '''
        @summary: should check configuration on whether we should blindly 
        relaunch and reconnect the controllers and take appropriate action
        @rtype: bool
        '''
        if self.relaunch_controllers:
            ''' let's blindly relaunch and reconnect controllers'''
            for controller_name, controller_data in self.controllers_data.iteritems():
                    print "Stopping tmux session"
                    self.stop_controller(controller_name)
                    self.wait(3)
                    self.destroy_tmux_session(controller_name)
                    self.wait(2)
                    print "Starting tmux session"
                    self.start_controller(controller_name)
                    self.wait(10)
                    print "Connecting controller"
                    self.connect_controller(controller_data['name'])
                    self.controllers_data[controller_name]['connected'] = self.controller_connected(controller_data['name'])
        
        ''' Now let's blindly connect all the controllers '''
        for controller_name, controller_data in self.controllers_data.iteritems():        
            self.connect_controller(controller_data['name'])
            
        ''' Let's only check whether controllers are connected'''
        for controller_name, controller_data in self.controllers_data.iteritems():        
            if self.controller_connected(controller_data['name']):
                print "Controller %s is connected" % controller_data['name']
                self.controllers_data[controller_name]['connected'] = True
            else:
                print "Controller %s is not connected." % controller_name
        
        '''If any controller failed to connect, we return False, otherwise True'''
        for controller_name, controller_data in self.controllers_data.iteritems():
            if controller_data['connected'] == False:
                return False
        
        return True
            
    
    @debug
    def all_controllers_connected(self):
        """
        @summary: Iterates over all controllers and makes sure they're connected
        """
        if self.connect_all_controllers():
            print "All controllers connected"
            return True
        else:
            help = self.produce_controllers_tmux_help()
            print "Could not connect all controllers - you should do it manually. Start and stop commands are here: %s" % help
            return False
        
    @debug
    def produce_controllers_tmux_help(self):
        help = {}
        controllers_list = self.config.get('global', 'controllers_list').split(',')
        for controller_name in controllers_list:
            help[controller_name] = {}
            help[controller_name]['stop_command'] = self.config.get(controller_name, 'stop_command')
            help[controller_name]['launch_command'] = self.config.get(controller_name, 'launch_command')
        return help
    
    @debug
    def prepare_container(self):
        for live_activity_group_name in self.relaunch_sequence:
            print "Adding live activity group: %s to relaunch queue" % live_activity_group_name
            live_activity_group = self.master.get_live_activity_group(
				{'live_activity_group_name' : live_activity_group_name})
            self.relaunch_container.append(live_activity_group)

    @debug
    def wait(self, interval=None):
        if interval:
            print "Waiting for %s seconds" % interval
            time.sleep(interval)
        else:
            print "Waiting for %s seconds" % self.interval_between_attempts
            time.sleep(self.interval_between_attempts)
        pass

    @debug
    def shutdown_all_activities(self):
        while self.stopped == False and self.shutdown_attempts >= 0:
            self.shutdown()
            self.wait()
            self.status_refresh()
            self.shutdown_attempts -= 1
            self.stopped = self.check_if_stopped()
            if self.stopped:
                break
            else:
                self.wait()
                print "Shutdown attempts left %s" % self.shutdown_attempts
    @debug
    def activate_all_live_activity_groups(self):
        while self.startup_attempts >= 0:
            self.activate()
            self.wait()
            self.status_refresh()
            self.relaunched = self.check_if_activated()
            if self.relaunched:
                return True
            else:
                print "Startup attempts left %s" % self.startup_attempts
                self.startup_attempts -= 1
                self.wait()
              
    @debug
    def loop_till_finished(self):
        '''
        @summary: first make sure we're stopped, then make sure we're activated
        '''
        if self.all_controllers_connected() and self.shutdown_all_activities() and self.activate_all_live_activity_groups():
            return True
        else:
            return False
        
    @debug
    def get_statuses(self):
        statuses = {}
        for live_activity_group_name in self.relaunch_sequence:
            print "Checking if '%s' group was successfully deactivated" % live_activity_group_name
            live_activity_group = self.master.get_live_activity_group(
                {'live_activity_group_name' : live_activity_group_name})
            for live_activity in live_activity_group.live_activities():
                statuses[live_activity.name()] = live_activity.status()
        print "Live activity statuses:"
        self.pp.pprint(statuses)
        return statuses

    @debug
    def check_if_stopped(self):
        statuses = self.get_statuses()
        statuses = {k: v for k, v in statuses.iteritems() if v != 'READY' }
        if statuses:
            print "Some activities could not get shut down %s" % statuses
            return False
        else:
            print "All activities shutdown"
            return True
    
    @debug
    def check_if_activated(self):
        statuses = self.get_statuses()
        for live_activity in [live_activity for live_activity in statuses.keys() if statuses[live_activity] == 'ACTIVE']:
            statuses.pop(live_activity)
        for live_activity in [live_activity for live_activity in statuses.keys() if statuses[live_activity] == 'RUNNING']:
            statuses.pop(live_activity)

        if statuses:
            print "Some activities could not get activated %s" % statuses
            return False
        else:
            print "All activities activated"
            return True

    @debug
    def shutdown(self):
        for live_activity_group in self.relaunch_container:
            live_activities = live_activity_group.live_activities()
            for live_activity in live_activities:
                print "Attempting a shut down of live_activity: %s " % live_activity.name()
                live_activity.send_shutdown()
                live_activity.send_clean_tmp()

    @debug
    def status_refresh(self):
        for live_activity_group in self.relaunch_container:
            live_activity_group.send_status_refresh()

    @debug
    def activate(self):
        for live_activity_group in self.relaunch_container:
            print "Attempting startup of live activity group %s" % live_activity_group.name()
            live_activity_group.send_activate()

    @debug
    def relaunch(self):
        self.prepare_container()
        if self.loop_till_finished() == True:
            print "Successully relaunched ispaces"
        else:
            print "Exiting: could not relaunch ispaces - look for errors in %s" % self.log_path

if __name__ == '__main__':
    config_path='/home/galadmin/etc/ispaces-client.conf'
    parser = OptionParser()
    parser.add_option("--config", dest="config_path", default="etc/ispaces-client.conf", help="Provie path to config file - ./etc/ispaces-client.conf by default", metavar="CONFIG_PATH")
    (options, args) = parser.parse_args()
    print "Using config file %s" % config_path
    if os.path.isfile(config_path):
        ir = InteractiveSpacesRelaunch(config_path)
        relaunched = ir.relaunch()
    else:
        print "Could not open config file %s" % config_path
