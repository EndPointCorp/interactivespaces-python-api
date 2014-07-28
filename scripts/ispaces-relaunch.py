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

'''
** it should have a config file
** it should iterate over live activity groups and perform a "deactivate => status => activate" loop as many times as needed
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
        self.interval_between_attempts = self.config.getint('relaunch', 'interval_between_attempts')
        self.log_path = self.config.get('global', 'logfile_path')
        self.pp = pprint.PrettyPrinter(indent=4)
        self.relaunch_sequence = self.config.get('relaunch', 'relaunch_sequence').split(',')

    @debug
    def prepare_container(self):
        for live_activity_group_name in self.relaunch_sequence:
            print "Adding live activity group: %s to relaunch queue" % live_activity_group_name
            live_activity_group = self.master.get_live_activity_group(
				{'live_activity_group_name' : live_activity_group_name})
            self.relaunch_container.append(live_activity_group)

    @debug
    def wait(self):
        print "Waiting for %s seconds" % self.interval_between_attempts
        time.sleep(self.interval_between_attempts)
        pass

    @debug
    def loop_till_finished(self):
        '''
        @summary: first make sure we're stopped, then make sure we're activated
        '''

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
                live_activity.send_shutdown()
                live_activity.send_clean_tmp()
        print "Shutting down"

    @debug
    def status_refresh(self):
        for live_activity_group in self.relaunch_container:
            live_activity_group.send_status_refresh()

    @debug
    def activate(self):
        for live_activity_group in self.relaunch_container:
            live_activity_group.send_activate()

    @debug
    def relaunch(self):
        self.prepare_container()
        if self.loop_till_finished() == True:
            print "Successully relaunched ispaces"
        else:
            print "Exiting: could not relaunch ispaces"

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
