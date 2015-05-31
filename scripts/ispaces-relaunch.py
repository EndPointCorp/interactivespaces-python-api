#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append("../")
sys.path.append("/home/galadmin/src/interactivespaces-python-api/")
import time
import json
import pprint
import urllib2
import argparse
import requests
import commands
import eventlet
import subprocess
import ConfigParser
from interactivespaces import Master
from interactivespaces import LiveActivityGroup
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

        #print("%s%s called [#%s]" % (indent, fc, call))
        __report_indent[0] += 1
        ret = fn(*params, **kwargs)
        __report_indent[0] -= 1
        #print("%s%s returned %s [#%s]" % (indent, fc, repr(ret), call))
        return ret
    wrap.callcount = 0
    return wrap


class InteractiveSpacesRelaunch(object):
    @debug
    def __init__(self, config_path, relaunch_options):
        self.config_path = config_path
        self.init_config(relaunch_options)
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

        if relaunch_options['full_relaunch'] or relaunch_options['full']:
            print colored("Performing full relaunch.", 'white', attrs=['bold'])
            self.relaunch_controllers = True
            self.relaunch_master = True

        if relaunch_options['master_only']:
            print colored("Performing relaunch of master only", 'white', attrs=['bold'])
            self.relaunch_controllers = False
            self.relaunch_master = True
            self.relaunch_live_activities = False

        if relaunch_options['controllers_only']:
            print colored("Performing relaunch of controllers only", 'white', attrs=['bold'])
            self.relaunch_controllers = True
            self.relaunch_master = False
            self.relaunch_live_activities = False

        if relaunch_options['live_activity_groups']:
            self.relaunch_sequence = relaunch_options['live_activity_groups'].split(',')
            if len(self.relaunch_sequence) == 0:
                print colored("Relaunch sequence is empty")
                sys.exit(1)
            print colored("Live activity groups to be relaunched: %s" % self.relaunch_sequence, 'white', attrs=['bold'])

        if relaunch_options['status']:
            print colored("Getting status of IS stack", 'white', attrs=['bold'])
        else:
            print colored("This is what's going to be launched:", 'white', attrs=['bold'])
            print "Controllers: %s" % self.relaunch_controllers
            print "Master: %s" % self.relaunch_master
            print "Live activities: %s" % self.relaunch_live_activities
            if self.relaunch_live_activities:
                print "Live activity groups: " + colored("%s" % (',').join(self.relaunch_sequence), 'magenta')

    @debug
    def init_config(self, relaunch_options):
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
        self.log_path = self.config.get('global', 'logfile_path')
        self.ssh_command = self.config.get('global', 'ssh_command')

        self.pp = pprint.PrettyPrinter(indent=4)

        self.controllers_data = self.init_controllers_config(relaunch_options)


    @debug
    def create_uri_for(self, location):
        return "http://" + self.host + ":" + self.port + location

    @debug
    def init_controllers_config(self, relaunch_options):
        config = {}
        if relaunch_options['controllers']:
            controllers_list = relaunch_options['controllers'].split(',')
        else:
            controllers_list = self.config.get('global', 'controllers_list').split(',')

        print colored("Controller(s) to relaunch: %s" % (',').join(controllers_list), 'green')

        for controller_name in controllers_list:
            config[controller_name] = {}
            config[controller_name]['name'] = self.config.get(controller_name, 'name')
            config[controller_name]['hostname'] = self.config.get(controller_name, 'hostname')
            config[controller_name]['stop_command'] = self.config.get(controller_name, 'stop_command')
            config[controller_name]['launch_command'] = self.config.get(controller_name, 'launch_command')
        return config

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
    def start_controller(self, controller_name):
        """
        @summary: starts controller
        @rtype: string containing start output
        """
        command = "%s %s '%s'" % (self.ssh_command, controller_name, self.controllers_data[controller_name]['launch_command'])
        cmd_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        output = cmd_process.communicate()[0].replace('\n', '').split(' ')
        return output

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
            return False
        except MasterException, e:
            return False
        except urllib2.HTTPError,e :
            print colored("Failed to communicate with master (%s) - is it running?" % e, 'red')


    @debug
    def connect_controller(self, controller_name):
        """
        @summary: connects controller through Master API and refreshes it's status.
        after that it will wait for the controller to appear as connected and runnning
        if controller does not appear as connected, this method will finally return False
        @rtype: bool
        """
        timeout = self.config.getint('relaunch', 'controllers_timeout')
        try:
            controller = self.master.get_space_controller({'space_controller_name': controller_name})
        except urllib2.HTTPError, e:
            print colored("Failed to connect to master (%s) - is it running?" % e, 'red')
            sys.exit(1)

        controller.send_connect()
        controller.send_status_refresh()

        for wait in xrange(0, timeout):
            if self.controller_connected(controller_name):
                print colored("Controller '%s' is connected" % controller_name, 'green')
                return True
            else:
                print colored('.', 'red'),
                time.sleep(1)
                sys.stdout.flush()
        print colored("Could not connect controller '%s' in specified timeout" % controller_name, 'red')
        print colored("Check if controller exists, started and whether the name is unique", 'red')
        return False

    @debug
    def controller_process_exists(self, controller_name):
        """
        @summary: returns True if process of a controller exists - False otherwise
        @rtype: bool
        """
        try:
            cmd = 'ssh %s -t "sudo supervisorctl status | grep interactivespaces_controller | grep RUNNING"' % controller_name
            out = subprocess.check_call(cmd, shell=True, stdout=subprocess.PIPE)
            return True
        except CalledProcessError, e:
            print "interactivespaces_controller supervisor process does not exist on %s" % controller_name
            return False

    @debug
    def relaunch_master_process(self):
        """
        @summary: relaunches master process and returns True as soon as the Master API is reachable
        @rtype: bool
        """
        cmd_process = subprocess.Popen(self.master_stop_command, shell=True, stdout=subprocess.PIPE)
        self.simple_wait('kill_master_process', 5)
        cmd_process = subprocess.Popen(self.master_launch_command, shell=True, stdout=subprocess.PIPE)
        if self.api_wait('start_master',
                          timeout=120,
                          url=self.create_uri_for(self.config.get('master', 'verify_url'))
                        ):
            return True
        else:
            return False
            print colored('Could not restart Interactivespaces Master within specified timeout', 'red')
            sys.exit(1)

    @debug
    def verify_controllers_sessions(self):
        """
        @summary: checks all controllers procesess and revives them if they dont exist
        """
        for controller_name, controller_data in self.controllers_data.iteritems():
            if self.controller_process_exists(controller_name):
                print colored("interactivespaces_controller supervisor process on %s exists" % controller_name, 'green')
            else:
                print colored("interactivespaces_controller supervisor process on %s does not exist - reviving" % controller_name, 'red')
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
                self.controllers_data[controller_name]['connected'] = True
            else:
                self.controllers_data[controller_name]['connected'] = False

        for controller_name, controller_data in self.controllers_data.iteritems():
            if self.controllers_data[controller_name]['connected']:
                pass
            else:
                return False

        return True

    @debug
    def verify_controllers_connected(self):
        print "Waiting for all controllers to come up with status: " + colored('RUNNING', 'green')
        timeout = self.config.get('relaunch', 'controllers_timeout')

        for blah in xrange(0, int(timeout)):
            if self.assert_controllers_api_statuses():
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
        self.verify_controllers_sessions()
        return self.verify_controllers_connected()

    @debug
    def controllers_connected(self):
        """
        @summary: Iterates over all controllers and makes sure they're connected
        """
        if self.connect_controllers():
            return True
        else:
            help = self.produce_controllers_help()
            print "Could not connect all controllers - use '--help'. Start and stop commands are here: %s" % help
            return False

    @debug
    def produce_controllers_help(self):
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
        print "Adding live activity groups to relaunch queue: "
        for live_activity_group_name in self.relaunch_sequence:
            print colored(" %s " % live_activity_group_name, 'magenta'),
            sys.stdout.flush()
            try:
                live_activity_group = self.master.get_live_activity_group(
				{'live_activity_group_name' : live_activity_group_name})
            except urllib2.HTTPError, e:
                print colored("Failed to communicate with master (%s)- is it running?" % e, 'red')
                sys.exit(1)

            self.relaunch_container.append(live_activity_group)

        print ""

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
    def simple_wait(self, info, timeout):
        """
        @summary: wait function with an info used for short sync'like sleep for freeing file descriptors:
        - killing java process
        - ???
        """
        print "Waiting for " + colored(self.interval_between_attempts, 'green') + " second(s) for " + colored(info, 'green')
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
            self.status_refresh()
            self.shutdown_attempts -= 1
            self.stopped = self.check_if_stopped()
            if self.stopped:
                return True
            else:
                print colored("Shutdown attempts left %s" % self.shutdown_attempts, 'red')
                sys.stdout.flush()
    @debug
    def activate_all_live_activity_groups(self):
        while self.startup_attempts >= 0:
            self.set_state()
            self.status_refresh()
            self.relaunched = self.check_if_activated()
            if self.relaunched:
                return True
            else:
                print colored("Startup attempts left %s" % self.startup_attempts, 'red')
                self.startup_attempts -= 1

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
            sys.stdout.flush()
            live_activity_group = self.master.get_live_activity_group(
                {'live_activity_group_name' : live_activity_group_name})
            if type(live_activity_group) == LiveActivityGroup:
                for live_activity in live_activity_group.live_activities():
                    statuses[live_activity.name()] = live_activity.status()
            else:
                print "Live activity group not found %s - please make sure that relaunch sequence contains existing group names" % live_activity_group_name
                sys.exit(1)
        return statuses

    @debug
    def check_if_stopped(self):
        """
        @summary: returns True if all live activities were stopped - False otherwise
        @rtype: bool
        """
        timeout = self.config.getint('relaunch', 'live_activities_timeout')
        print colored("Waiting for live activities to stop", "green")
        for wait in xrange(0, timeout):
            time.sleep(1)
            statuses = self.get_statuses()
            statuses = {k: v for k, v in statuses.iteritems() if v != 'READY' }
            statuses = {k: v for k, v in statuses.iteritems() if v != 'DOESNT_EXIST' }

            if statuses:
                print colored(".", 'red'),
                sys.stdout.flush()
            else:
                print colored("All activities have been succesfully shutdown", 'green')
                return True

        print ""
        print colored("Giving up - following live activities could not be shut down:", 'red')
        self.pp.pprint(statuses)
        return False

    @debug
    def check_if_activated(self):
        """
        @summary: returnes True if all activites got status "ACTIVE" or "RUNNING". It will poll and wait for a while
        for each activity
        @rtype: bool
        """
        timeout = self.config.getint('relaunch', 'live_activities_timeout')
        print colored("Waiting for live activities to start", "green")

        for wait in xrange(0, timeout):
            statuses = self.get_statuses()
            for live_activity in [live_activity for live_activity in statuses.keys() if statuses[live_activity] == 'ACTIVE']:
                statuses.pop(live_activity)
            for live_activity in [live_activity for live_activity in statuses.keys() if statuses[live_activity] == 'RUNNING']:
                statuses.pop(live_activity)

            if statuses:
                print colored(".", 'red'),
                sys.stdout.flush()
                time.sleep(1)
            else:
                print colored("All activities activated", 'green')
                return True
        print colored("Following live activities could not get activated:", 'red')
        self.pp.pprint(statuses)
        return False

    @debug
    def shutdown(self):
        """
        @summary: shuts down all activities from teh .relaunch_container - in addition it will clean la's tmp
        @rtype: bool
        """
        print "Attempting shutdown of live activities:"
        for live_activity_group in self.relaunch_container:
            live_activities = live_activity_group.live_activities()
            for live_activity in live_activities:
                print colored(" %s " % live_activity.name(), 'magenta'),
                sys.stdout.flush()
                live_activity.send_shutdown()
                live_activity.send_clean_tmp()
        print ""
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
    def set_state(self):
        """
        @summary: sets activated/running state all live activity groups by deploying, configuring and activating them
        """
        print colored("Attempting (D)eploy -> (C)onfigure -> (S)tartup -> (A)ctivate of live activity groups:", 'green')
        for live_activity_group in self.relaunch_container:
            print colored(" %s " % live_activity_group.name(), 'magenta'),
            sys.stdout.flush()
            print colored("D", 'blue'),
            sys.stdout.flush()
            live_activity_group.send_deploy()
            print colored("C", 'blue'),
            sys.stdout.flush()
            live_activity_group.send_configure()

            desired_state = self.config.get('relaunch_states', live_activity_group.name())

            if desired_state == 'activate':
                live_activity_group.send_activate()
                print colored("A", 'blue')
                sys.stdout.flush()
            elif desired_state == 'startup':
                live_activity_group.send_startup()
                print colored("S", 'blue')
                sys.stdout.flush()
            else:
                live_activity_group.send_activate()
                print colored("A", 'blue')
                sys.stdout.flush()


        print ""

    @debug
    def relaunch_controllers_processes(self):
        """
        @summary: stop controllers processes and starts them afterwards.
        No asserts are made in the API
        @rtype: bool
        """
        for controller_name, controller_data in self.controllers_data.iteritems():
                self.stop_controller(controller_name)
                self.simple_wait("Waiting for java process to exit", 5)
                print "Connecting controller %s on %s" % (controller_data['name'], controller_name)

        self.simple_wait("Waiting for controllers to free file descriptors", 3)

        print colored("Launching controllers", 'green')
        for controller_name, controller_data in self.controllers_data.iteritems():
                self.start_controller(controller_name)

        self.simple_wait("Waiting for controllers to come up", 3)
        for controller_name, controller_data in self.controllers_data.iteritems():
                self.connect_controller(controller_data['name'])
                self.controllers_data[controller_name]['connected'] = self.controller_connected(controller_data['name'])
        return True

    @debug
    def _check_relaunch_sequence(self, interactivespaces):
        """
        @summary: checks whether all live activity groups are on relaunch_sequence and whether all
        relaunch sequence items are configured are referring to existing live activity groups
        """

        relaunch_sequence = []

        for item in interactivespaces['ispaces_client']['relaunch_sequence']:
            if (type(item) == str) or (type(item) == unicode):
                relaunch_sequence.append(item)
            elif type(item) == dict:
                relaunch_sequence.append(item['name'])

        for live_activity_group_name in interactivespaces['live_activity_groups'].keys():
            if live_activity_group_name in relaunch_sequence:
                print colored("OK: %s is on relaunch list" % live_activity_group_name, "green")
            else:
                print colored("WARN: %s is not on relaunch list" % live_activity_group_name, "yellow")

        for live_activity_group_name in relaunch_sequence:
            if live_activity_group_name in interactivespaces['live_activity_groups'].keys():
                print colored("OK: %s in relaunch sequence exists in live activity groups list " % live_activity_group_name, "green")
            else:
                print colored("WARN: %s does not seem to be existing live activity group" % live_activity_group_name, "yellow")

        print ""

    def _check_live_activities(self, interactivespaces):
        """
        @summary: checks:
        - whether all live activities that are members of live activity groups exist
        - whether all live activities assigned to controllers exist in live activity groups
        """
        for space_controller_name, space_controller_data in interactivespaces['controllers'].iteritems():
            """
            For every space controller create a list of live activities assigned to it
            """
            print
            print colored("Controller name:", "white"),
            print colored("%s" % space_controller_name, 'white', attrs=['bold'])
            sc_live_activities = [ la for la in interactivespaces['live_activities'].iteritems() if la[1]['controller'] == space_controller_name ]

            controller_assigned_live_activities = {}

            for la in sc_live_activities:
                controller_assigned_live_activities[la[0]] = la[1]['controller']

            """
            For every live activity group create a list of live activities assigned to this controller
            """

            live_activity_groups_assigned_live_activities = {}

            for live_activity_group_name, live_activity_group_data in interactivespaces['live_activity_groups'].iteritems():
                live_activities = [ la for la in live_activity_group_data['live_activities'] if la['space_controller_name'] == space_controller_name ]
                for la in live_activities:
                    live_activity_groups_assigned_live_activities[la['live_activity_name']] = la['space_controller_name']
                    print colored("  Live activity:", "white"),
                    print colored("%s" % la['live_activity_name'], "green"),
                    print colored("(Group: %s)" % live_activity_group_name, "magenta")
                    sys.stdout.flush()

            identical = (controller_assigned_live_activities == live_activity_groups_assigned_live_activities)

            if identical:
                print
                print colored("  Live Activities assigned to controller match Live Activities in Live Activity Groups", "green")
            else:
                diff = set(controller_assigned_live_activities.keys()) - set(live_activity_groups_assigned_live_activities.keys())
                print colored("LA's from SC are different from LAG's LA's. Here's the difference: %s" % diff, "red")

                print colored("Controller live activities: %s" % controller_assigned_live_activities, "white")
                print colored("Live activity group live activities: %s" % live_activity_groups_assigned_live_activities, "white")

    @debug
    def _check_viewports(self, interactivespaces, liquid_galaxy):
        """
        @summary: checks whether all viewports mentioned in the configuration match viewports configured on a display node
        """
        print
        print colored("Checking viewports", "white")
        print

        for live_activity_name, live_activity_data in interactivespaces['live_activities'].iteritems():
            try:
                live_activity_viewports = live_activity_data['config']['lg.window.viewport.target'].strip().split(',')
                live_activity_viewports = [ v.strip() for v in live_activity_viewports]
                dispnode_name = live_activity_data['controller']
                dispnode = [ d for d in liquid_galaxy['display_nodes'] if d['hostname'] == dispnode_name ][0]
                dispnode_viewports = [ screen['name'] for screen in dispnode['screens'] ]
                for viewport in live_activity_viewports:
                    if viewport not in dispnode_viewports:
                        print colored("  Viewport name '%s' on live activity: %s is not configured on dispnode %s" % (viewport, live_activity_name, dispnode_name), "yellow")
                    else:
                        print colored("  OK: %s => %s" % (live_activity_name, viewport), "green")
            except Exception, e:
                pass


    @debug
    def check_config(self):
        """
        @summary: validates the config. Iterates over all controllers and prints live activities assigned to them.
        Will print warning if live activity does not belong to any live activity group.
        """
        with open('/home/galadmin/etc/node.json', 'r') as node:
            node_definition = json.loads(node.read())
            interactivespaces = node_definition['interactivespaces']
            liquid_galaxy = node_definition['liquid_galaxy']

        self._check_relaunch_sequence(interactivespaces)
        self._check_live_activities(interactivespaces)
        self._check_viewports(interactivespaces, liquid_galaxy)

    @debug
    def get_status(self):
        """
        @summary: gets live activities statuses
        """
        print colored('Live activities', 'green')
        self.pp.pprint(self.get_statuses())
        print colored('Space controllers state', 'green')
        self.assert_controllers_api_statuses()

    @debug
    def relaunch(self):
        if self.relaunch_master:
            self.relaunch_master_process()

        if self.relaunch_controllers:
            self.relaunch_controllers_processes()

        if self.relaunch_live_activities:
            self.prepare_container()
            if self.loop_till_finished() == True:
                print colored("Successfully relaunched ispaces", 'green', attrs=['bold'])
                sys.exit(0)
            else:
                print colored("Exiting: could not relaunch ispaces - look for errors in %s and 'ugly' interface" % self.log_path, 'red')
                sys.exit(1)

if __name__ == '__main__':
    """
    @summary: parse all arguments and check whether user is asking for a status or a relaunch
    """
    parser = argparse.ArgumentParser(description='Relaunch interactivespaces')
    parser.add_argument("--full-relaunch", help="Additionally relaunch controllers and master process", action="store_true")
    parser.add_argument("--full", help="Alias for --full-relaunch", action="store_true")
    parser.add_argument("--master-only", help="Relaunch the master process only - remember to relaunch controllers after that", action="store_true")
    parser.add_argument("--controllers-only", help="Relaunch the controllers only", action="store_true")
    parser.add_argument("--controllers", help="Comma separated of controllers to restart e.g. : --controllers=42-a,42-b,42-c (works with --controllers-only only)")
    parser.add_argument("--no-live-activities", help="Don't relaunch live activities", action="store_true")
    parser.add_argument("--config", help="Provide path to config file - /home/galadmin/etc/ispaces-client.conf by default")
    parser.add_argument("--live-activity-groups", help="Provide quoted, comma-delimited names of live activity groups to manage e.g. --live-activity-groups='Touchscreen Browser','Media Services' ")
    parser.add_argument("--status", help="Print current status of managed live activities.", action="store_true")
    parser.add_argument("--check-config", help="Check the configuration", action="store_true")

    args = parser.parse_args()

    relaunch_options = { 'full_relaunch': args.full_relaunch,
                         'full': args.full,
                         'master_only': args.master_only,
                         'controllers_only': args.controllers_only,
                         'controllers': args.controllers,
                         'no_live_activities': args.no_live_activities,
                         'live_activity_groups': args.live_activity_groups,
                         'status': args.status,
                         'check_config': args.check_config
                         }

    if args.config:
        config_path = args.config
    else:
        config_path = '/home/galadmin/etc/ispaces-client.conf'
    if os.path.isfile(config_path):
        ir = InteractiveSpacesRelaunch(config_path, relaunch_options)
        if relaunch_options['status']:
            ir.get_status()
        elif relaunch_options['check_config']:
            ir.check_config()
        else:
            ir.relaunch()
    else:
        print "Could not open config file %s" % config_path
