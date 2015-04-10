#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append("../")
sys.path.append("/home/galadmin/src/interactivespaces-python-api/")
from interactivespaces import Master
import ConfigParser
import argparse
import pprint
import time
import subprocess
from subprocess import CalledProcessError
from interactivespaces.exception import ControllerNotFoundException

'''
TODO:
- refactor connect_all_controllers()
- manage sys.path in the appropriate way without hardcoded paths and .append()
- make config file steer the debug level for the @debug decorator
- make support for restarting one controller
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

        # print("%s%s called [#%s]" % (indent, fc, call))
        __report_indent[0] += 1
        ret = fn(*params, **kwargs)
        __report_indent[0] -= 1
        # print("%s%s returned %s [#%s]" % (indent, fc, repr(ret), call))
        return ret
    wrap.callcount = 0
    return wrap


class InteractiveSpacesRelaunch(object):
    @debug
    def __init__(self, config_path, relaunch_options):
        self.config_path = config_path
        self.init_config()
        self.master = Master(host=self.host,
                             port=self.port,
                             logfile_path=self.log_path)
        self.relaunch_container = []
        self.stopped = False
        self.activated = False

        # Parsing arguments takes precedence over config file options
        if relaunch_options['full_relaunch']:
            print "Performing full relaunch."
            self.relaunch_controllers = True
            self.relaunch_master = True
        if relaunch_options['master_only']:
            print "Performing relaunch of master"
            self.relaunch_controllers = False
            self.relaunch_master = True
        if relaunch_options['controllers_only']:
            print "Performing relaunch of master"
            self.relaunch_controllers = True
            self.relaunch_master = False
        if relaunch_options['no_live_activities']:
            print "Performing relaunch without relaunching live activities"
            self.relaunch_live_activities = False
        else:
            self.relaunch_live_activities = True


    @debug
    def init_config(self):
        self.config = ConfigParser.RawConfigParser()
        self.config.read(self.config_path)
        self.host = self.config.get('master', 'host')
        self.port = self.config.get('master', 'port')
        self.shutdown_attempts = self.config.getint('relaunch',
                                                    'shutdown_attempts')
        self.startup_attempts = self.config.getint('relaunch',
                                                   'startup_attempts')
        self.relaunch_sequence = self.config.get('relaunch',
                                                 'relaunch_sequence').split(',')
        self.interval_between_attempts = self.config.getint('relaunch',
                                                            'interval_between_attempts')
        self.relaunch_controllers = self.config.getint('relaunch',
                                                       'relaunch_controllers')
        self.relaunch_master = self.config.getint('relaunch',
                                                  'relaunch_master')
        self.master_stop_command = self.config.get('master',
                                                   'stop_command')
        self.master_launch_command = self.config.get('master',
                                                     'launch_command')
        self.master_destroy_tmux_command = self.config.get('master',
                                                           'destroy_tmux_command')
        self.log_path = self.config.get('global',
                                        'logfile_path')
        self.ssh_command = self.config.get('global',
                                           'ssh_command')
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
        cmd_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        output = cmd_process.communicate()[0].replace('\n', '').split(' ')
        return output

    @debug
    def destroy_tmux_session(self, controller_name):
        command = "%s %s '%s'" % (self.ssh_command, controller_name, self.controllers_data[controller_name]['destroy_tmux_command'])
        cmd_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        output = cmd_process.communicate()[0].replace('\n', '').split(' ')
        return output

    @debug
    def start_controller(self, controller_name):
        command = "%s %s '%s'" % (self.ssh_command, controller_name, self.controllers_data[controller_name]['launch_command'])
        cmd_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        output = cmd_process.communicate()[0].replace('\n', '').split(' ')
        return output

    @debug
    def connect_controller(self, controller_name):
        controller = self.master.get_space_controller({'space_controller_name': controller_name})
        controller.send_connect()
        self.wait('connect_controller', 3)
        controller.send_status_refresh()
        pass

    @debug
    def controller_tmux_session_exists(self, controller_name):
        try:
            cmd = 'ssh %s -t "tmux ls | grep ISController"' % controller_name
            out = subprocess.check_call(cmd, shell=True)
            return True
        except CalledProcessError, e:
            print "tmux session ISController does not exist on %s" % controller_name
            return False

    @debug
    def relaunch_master_process(self):
        print "Killing master process"
        cmd_process = subprocess.Popen(self.master_stop_command, shell=True, stdout=subprocess.PIPE)
        self.wait('relaunch_master', 3)
        print "Destroying master tmux"
        cmd_process = subprocess.Popen(self.master_destroy_tmux_command, shell=True, stdout=subprocess.PIPE)
        self.wait('relaunch_master', 1)
        print "Launching master and waiting for the process to come up"
        cmd_process = subprocess.Popen(self.master_launch_command, shell=True, stdout=subprocess.PIPE)
        self.wait('relaunch_master', 20)
        pass

    @debug
    def connect_all_controllers(self):
        '''
        @summary: should check configuration on whether we should blindly 
        relaunch and reconnect the controllers and take appropriate action
        @rtype: bool
        '''

        ''' Check whether tmux sessions are up'''
        for controller_name, controller_data in self.controllers_data.iteritems():
            if self.controller_tmux_session_exists(controller_name):
                print "Tmux session ISController on %s exists" % controller_name
            else:
                print "Tmux session ISController on %s does not exist - reviving" % controller_name
                self.start_controller(controller_name)
                self.wait('start controller', 10)
                print "Connecting controller %s on %s" % (controller_data['name'], controller_name)
                self.connect_controller(controller_data['name'])
                self.controllers_data[controller_name]['connected'] = self.controller_connected(controller_data['name'])

        ''' Now let's blindly connect all the controllers'''
        for controller_name, controller_data in self.controllers_data.iteritems():
            self.connect_controller(controller_data['name'])

        ''' Let's only check whether controllers are connected and ready'''
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
    def wait(self, info, interval=None,):
        if interval:
            print "Waiting for %s seconds (%s)" % (interval, info)

            time.sleep(interval)
        else:
            print "Waiting for %s seconds (%s)" % (self.interval_between_attempts, info)
            time.sleep(self.interval_between_attempts)
        pass

    @debug
    def shutdown_all_activities(self):
        while self.stopped == False and self.shutdown_attempts >= 0:
            self.shutdown()
            self.wait('shutdown_all_activities')
            self.status_refresh()
            self.shutdown_attempts -= 1
            self.stopped = self.check_if_stopped()
            if self.stopped:
                return True
            else:
                self.wait('shutdown_all_activities')
                print "Shutdown attempts left %s" % self.shutdown_attempts
    @debug
    def activate_all_live_activity_groups(self):
        while self.startup_attempts >= 0:
            self.activate()
            self.wait('activate_all_live_activity_groups')
            self.status_refresh()
            self.relaunched = self.check_if_activated()
            if self.relaunched:
                return True
            else:
                print "Startup attempts left %s" % self.startup_attempts
                self.startup_attempts -= 1
                self.wait('activate_all_live_activity_groups')

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
            print "All activities have been succesfully shutdown"
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
                print "Attempting shutdown of live activity: %s " % live_activity.name()
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
    def relaunch_controllers_processes(self):
        ''' let's blindly relaunch and reconnect controllers'''
        for controller_name, controller_data in self.controllers_data.iteritems():
                print "Stopping tmux session on %s" % controller_name
                self.stop_controller(controller_name)
                self.wait('relaunch_controllers:stop controller', 3)
                self.destroy_tmux_session(controller_name)
                self.wait('destroy tmux session', 2)
                print "Starting tmux session on %s" % controller_name
                self.start_controller(controller_name)
                self.wait('start controller', 10)
                print "Connecting controller %s on %s" % (controller_data['name'], controller_name)
                self.connect_controller(controller_data['name'])
                self.controllers_data[controller_name]['connected'] = self.controller_connected(controller_data['name'])


    @debug
    def relaunch(self):
        if self.relaunch_master:
            self.relaunch_master_process()

        if self.relaunch_controllers:
            self.relaunch_controllers_processes()

        if self.relaunch_live_activities:
            self.prepare_container()
            if self.loop_till_finished() == True:
                print "Successully relaunched ispaces"
            else:
                print "Exiting: could not relaunch ispaces - look for errors in %s" % self.log_path

if __name__ == '__main__':
    os.unsetenv('TMUX')
    parser = argparse.ArgumentParser(description='Relaunch interactivespaces')
    parser.add_argument("--full-relaunch", help="Additionally relaunch controllers and master process", action="store_true")
    parser.add_argument("--master-only", help="Relaunch the master process only", action="store_true")
    parser.add_argument("--controllers-only", help="Relaunch the controllers only", action="store_true")
    parser.add_argument("--no-live-activities", help="Don't relaunch live activities", action="store_true")
    parser.add_argument("--config", help="Provide path to config file - /home/galadmin/etc/ispaces-client.conf by default")

    args = parser.parse_args()

    relaunch_options = { 'full_relaunch': args.full_relaunch,
                         'master_only': args.master_only,
                         'controllers_only': args.controllers_only,
                         'no_live_activities': args.no_live_activities
                         }

    print 'Relaunch options: %s' % relaunch_options

    if args.config:
        config_path = args.config
    else:
        config_path = '/home/galadmin/etc/ispaces-client.conf'
    if os.path.isfile(config_path):
        ir = InteractiveSpacesRelaunch(config_path, relaunch_options)
        relaunched = ir.relaunch()
    else:
        print "Could not open config file %s" % config_path
