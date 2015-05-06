#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append("../")
sys.path.append("/home/galadmin/src/interactivespaces-python-api/")
import time
import json
import pprint
import argparse
import requests
import commands
import eventlet
import subprocess
import ConfigParser
from interactivespaces import Master
from termcolor import colored
from subprocess import CalledProcessError
from interactivespaces.exception import ControllerNotFoundException


eventlet.monkey_patch()
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
        self.relaunch_live_activities = True
        self.relaunch_controllers = False
        self.relaunch_master = False

        if relaunch_options['no_live_activities']:
            print "Performing relaunch without relaunching live activities"
            self.relaunch_live_activities = False
        else:
            self.relaunch_live_activities = True
        if relaunch_options['full_relaunch']:
            print "Performing full relaunch."
            self.relaunch_controllers = True
            self.relaunch_master = True
        if relaunch_options['master_only']:
            print "Performing relaunch of master"
            self.relaunch_controllers = False
            self.relaunch_master = True
            self.relaunch_live_activities = False
        if relaunch_options['controllers_only']:
            print "Performing relaunch of master"
            self.relaunch_controllers = True
            self.relaunch_master = False
            self.relaunch_live_activities = False

        print colored("This is what's going to be launched:", 'white')
        print colored("Controllers => %s" % self.relaunch_controllers, 'green')
        print colored("Master => %s" % self.relaunch_master, 'green')
        print colored("Live activities => %s" % self.relaunch_live_activities, 'green')



    @debug
    def init_config(self):
        self.config = ConfigParser.RawConfigParser()
        self.config.read(self.config_path)
        self.host = self.config.get('master', 'host')
        self.port = self.config.get('master', 'port')
        self.shutdown_attempts = self.config.getint('relaunch','shutdown_attempts')
        self.startup_attempts = self.config.getint('relaunch','startup_attempts')
        self.relaunch_sequence = self.config.get('relaunch','relaunch_sequence').split(',')
        self.interval_between_attempts = self.config.getint('relaunch','interval_between_attempts')
        self.relaunch_controllers = self.config.getint('relaunch','relaunch_controllers')
        self.relaunch_master = self.config.getint('relaunch', 'relaunch_master')
        self.master_stop_command = self.config.get('master', 'stop_command')
        self.master_launch_command = self.config.get('master', 'launch_command')
        self.master_destroy_tmux_command = self.config.get('master', 'destroy_tmux_command')
        self.log_path = self.config.get('global', 'logfile_path')
        self.ssh_command = self.config.get('global', 'ssh_command')

        self.pp = pprint.PrettyPrinter(indent=4)

        self.controllers_data = self.init_controllers_config()

    @debug
    def create_uri_for(self, location):
        return "http://" + self.host + ":" + self.port + location

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
        """
        @summary: stops a remote controller process
        @rtype: string containing output of stop command
        """
        command = "%s %s '%s'" % (self.ssh_command, controller_name, self.controllers_data[controller_name]['stop_command'])
        cmd_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        output = cmd_process.communicate()[0].replace('\n', '').split(' ')
        return output

    @debug
    def destroy_tmux_session(self, controller_name):
        """
        @summary: destroys tmux session of a controller
        @rtype: string with command output
        """
        command = "%s %s '%s'" % (self.ssh_command, controller_name, self.controllers_data[controller_name]['destroy_tmux_command'])
        cmd_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        output = cmd_process.communicate()[0].replace('\n', '').split(' ')
        return output

    @debug
    def start_controller(self, controller_name):
        """
        @summary: starts controller (most likely a tmux session)
        @rtype: string containing start output
        """
        command = "%s %s '%s'" % (self.ssh_command, controller_name, self.controllers_data[controller_name]['launch_command'])
        cmd_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        output = cmd_process.communicate()[0].replace('\n', '').split(' ')
        self.simple_wait('start_controller',
                         timeout=1)
        return output

    @debug
    def connect_controller(self, controller_name):
        """
        @summary: connects controller through Master API and refreshes it's status
        """
        controller = self.master.get_space_controller({'space_controller_name': controller_name})
        controller.send_connect()
        self.simple_wait('connect_controller', 1)
        controller.send_status_refresh()

    @debug
    def controller_tmux_session_exists(self, controller_name):
        """
        @summary: returns True if tmux session of a controller exists - False otherwise
        @rtype: bool
        """
        try:
            cmd = 'ssh %s -t "tmux ls | grep ISController"' % controller_name
            out = subprocess.check_call(cmd, shell=True)
            return True
        except CalledProcessError, e:
            print "tmux session ISController does not exist on %s" % controller_name
            return False

    @debug
    def relaunch_master_process(self):
        """
        @summary: relaunches master process and returns True as soon as the Master API is reachable
        @rtype: bool
        """
        self.simple_wait('kill_master_process', 1)
        cmd_process = subprocess.Popen(self.master_stop_command, shell=True, stdout=subprocess.PIPE)
        self.simple_wait('destroy_master_tmux', 1)
        cmd_process = subprocess.Popen(self.master_destroy_tmux_command, shell=True, stdout=subprocess.PIPE)
        cmd_process = subprocess.Popen(self.master_launch_command, shell=True, stdout=subprocess.PIPE)
        if self.api_wait('start_master',
                          timeout=60,
                          url=self.create_uri_for(self.config.get('master', 'verify_url'))
                        ):
            return True
        else:
            return False

    @debug
    def verify_controllers_tmux_sessions(self):
        """
        @summary: checks all controllers tmux sessions and revives them if they dont exist
        """
        for controller_name, controller_data in self.controllers_data.iteritems():
            if self.controller_tmux_session_exists(controller_name):
                print "Tmux session ISController on %s exists" % controller_name
            else:
                print "Tmux session ISController on %s does not exist - reviving" % controller_name
                self.start_controller(controller_name)
                print "Connecting controller %s on %s" % (controller_data['name'], controller_name)
                self.connect_controller(controller_data['name'])
                self.controllers_data[controller_name]['connected'] = self.controller_connected(controller_data['name'])

    @debug
    def assert_controllers_api_statuses(self):
        """
        @summary: checks whether all controllers are running by connecting them and making an
        assert on every one of them thru Master API.
        @rtype: bool
        """
        for controller_name, controller_data in self.controllers_data.iteritems():
            self.connect_controller(controller_data['name'])
            if self.controller_connected(controller_data['name']):
                print colored("Controller %s is connected!" % controller_data['name'], 'green')
                self.controllers_data[controller_name]['connected'] = True
            else:
                self.controllers_data[controller_name]['connected'] = False

        for controller_name, controller_data in self.controllers_data.iteritems():
            if self.controllers_data[controller_name]['connected']:
                pass
            else:
                print colored("Controller %s is not connected!" % controller_name, 'red')
                return False

        return True

    @debug
    def verify_controllers_connected(self, info):
        print "Waiting for all controllers to come up with status: " + colored('RUNNING', 'green')
        timeout = self.config.get('relaunch', 'controllers_timeout')

        for blah in xrange(0, timeout):
            if self.assert_controllers_api_statuses():
                print colored("All controllers connected!", 'green')
                sys.stdout.flush()
                return True
            else:
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(1)

        print colored('Waiting timed out :(', 'red')
        return False

    @debug
    def connect_controllers(self):
        """
        @summary: should verify all connections and try to revive them if they're not connected
        After that controllers should be visible as "Connected" in Master API.
        @rtype: bool
        """
        self.verify_controllers_tmux_sessions()
        return self.verify_controllers_connected()

    @debug
    def controllers_connected(self):
        """
        @summary: Iterates over all controllers and makes sure they're connected
        """
        if self.connect_controllers():
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
        """
        @summary: prepares a list of live activity API objects to relaunch
        @rtype: bool
        """
        for live_activity_group_name in self.relaunch_sequence:
            print "Adding live activity group: %s to relaunch queue" % live_activity_group_name
            live_activity_group = self.master.get_live_activity_group(
				{'live_activity_group_name' : live_activity_group_name})
            self.relaunch_container.append(live_activity_group)

        return True

    @debug
    def assert_api_url_status(self, url, http_status_code=200, timeout=5):
        """
        @summary: method used to make asserts on an API. It returns true if API under `url`
        returned `http_status_code` within specified `timeout` with JSON that's parseable
        @rtype: bool
        """
        try:
            with eventlet.Timeout(timeout):
                try:
                    url = url.strip('"')
                    #print "Getting URL %s" % url
                    response = requests.get(url)
                    print 'HTTP %s' % response.status_code,
                except Exception:
                    return False
                if response.status_code == http_status_code:
                    try:
                        json.loads(response.content)
                        print colored(' API JSON is valid. ', 'green'),
                    except Exception:
                        print colored(' JSON returned by API is not parseable ', 'red'),
                        return False
                    return True
                else:
                    return False
        except eventlet.timeout.Timeout:
            print colored('%s timed out' % url, 'red')
            return False

    @debug
    def simple_wait(self, info, timeout)
        """
        @summary: wait function with an info used for short sync'like sleep for freeing file descriptors:
        - destroying tmuxes
        - killing java process
        - ???
        """
        print "Waiting for " + colored(self.interval_between_attempts, 'green') + " seconds for " + colored(info, 'green')
        time.sleep(self.interval_between_attempts)

    @debug
    def api_wait(self, info, timeout=None, url=None):
        print "Waiting for the webservice to come up with: " + colored('200 OK', 'green')
        for blah in xrange(0, timeout):
            if self.assert_api_url_status(url):
                print colored("Service is up (%s)" % info, 'green')
                sys.stdout.flush()
                return True
            else:
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(1)
        print colored('Waiting timed out :(', 'red')
        return False

    @debug
    def shutdown_all_activities(self):
        while self.stopped == False and self.shutdown_attempts >= 0:
            self.shutdown()
            self.simple_wait('shutdown_all_activities')
            self.status_refresh()
            self.shutdown_attempts -= 1
            self.stopped = self.check_if_stopped()
            if self.stopped:
                return True
            else:
                self.simple_wait('shutdown_all_activities')
                print "Shutdown attempts left %s" % self.shutdown_attempts
    @debug
    def activate_all_live_activity_groups(self):
        while self.startup_attempts >= 0:
            self.activate()
            self.simple_wait('activate_all_live_activity_groups')
            self.status_refresh()
            self.relaunched = self.check_if_activated()
            if self.relaunched:
                return True
            else:
                print "Startup attempts left %s" % self.startup_attempts
                self.startup_attempts -= 1
                self.simple_wait('activate_all_live_activity_groups')

    @debug
    def loop_till_finished(self):
        '''
        @summary: first make sure we're stopped, then make sure we're activated
        '''
        if self.controllers_connected() and self.shutdown_all_activities() and self.activate_all_live_activity_groups():
            return True
        else:
            return False

    @debug
    def get_statuses(self):
        """
        @summary: checks for live activities statuses and returns them
        @rtype: dict
        """
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
        """
        @summary: returns True if all live activities were stopped - False otherwise
        @rtype: bool
        """
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
        """
        @summary: returnes True if all activites got activated
        @rtype: bool
        """
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
        """
        @summary: shuts down all activities from teh .relaunch_container
        @rtype: bool
        """

        for live_activity_group in self.relaunch_container:
            live_activities = live_activity_group.live_activities()
            for live_activity in live_activities:
                print "Attempting shutdown of live activity: %s " % live_activity.name()
                live_activity.send_shutdown()
                live_activity.send_clean_tmp()
        return True

    @debug
    def status_refresh(self):
        """
        @summary: sends 'status' refresh request to live activity groups that
        were listed in .relaunch_container
        """
        for live_activity_group in self.relaunch_container:
            live_activity_group.send_status_refresh()

    @debug
    def activate(self):
        for live_activity_group in self.relaunch_container:
            print "Attempting startup of live activity group %s" % live_activity_group.name()
            live_activity_group.send_activate()

    @debug
    def relaunch_controllers_processes(self):
        """
        @summary: stop controllers processes (most likely tmux sessions) and starts them afterwards.
        No asserts are made in the API
        @rtype: bool
        """
        for controller_name, controller_data in self.controllers_data.iteritems():
                self.stop_controller(controller_name)
                self.simple_wait('stop_controller', 1)
                self.destroy_tmux_session(controller_name)
                self.simple_wait('destroy tmux session', 1)
                self.start_controller(controller_name)
                print "Connecting controller %s on %s" % (controller_data['name'], controller_name)
                self.connect_controller(controller_data['name'])
                self.controllers_data[controller_name]['connected'] = self.controller_connected(controller_data['name'])
        return True

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
    parser.add_argument("--master-only", help="Relaunch the master process only - remember to relaunch controllers after that", action="store_true")
    parser.add_argument("--controllers-only", help="Relaunch the controllers only", action="store_true")
    parser.add_argument("--no-live-activities", help="Don't relaunch live activities", action="store_true")
    parser.add_argument("--config", help="Provide path to config file - /home/galadmin/etc/ispaces-client.conf by default")

    args = parser.parse_args()

    relaunch_options = { 'full_relaunch': args.full_relaunch,
                         'master_only': args.master_only,
                         'controllers_only': args.controllers_only,
                         'no_live_activities': args.no_live_activities
                         }

    if args.config:
        config_path = args.config
    else:
        config_path = '/home/galadmin/etc/ispaces-client.conf'
    if os.path.isfile(config_path):
        ir = InteractiveSpacesRelaunch(config_path, relaunch_options)
        relaunched = ir.relaunch()
    else:
        print "Could not open config file %s" % config_path
