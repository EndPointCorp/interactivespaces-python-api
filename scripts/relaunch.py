#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append("../")
from interactivespaces import Master
import ConfigParser

'''
** it should have a config file
** it should iterate over live activity groups and perform a "deactivate => status => activate" loop as many times as needed
'''

__report_indent=[0]

def debug(fn):
    def wrap(*params,**kwargs):
        call = wrap.callcount = wrap.callcount + 1

        indent = ' ' * __report_indent[0]
        fc = "%s(%s)" % (fn.__name__, ', '.join(
            [a.__repr__() for a in params] +
            ["%s = %s" % (a, repr(b)) for a,b in kwargs.items()]
        ))

        print("%s%s called [#%s]" % (indent, fc, call))
        __report_indent[0] += 1
        ret = fn(*params,**kwargs)
        __report_indent[0] -= 1
        print("%s%s returned %s [#%s]" % (indent, fc, repr(ret), call))
        return ret
    wrap.callcount = 0
    return wrap


class InteractiveSpacesRelaunch(object):
    def __init__(self):
        self.init_config()
	self.master = Master(self.host, self.port)
	self.relaunch_sequence = self.config.get('relaunch', 'relaunch_sequence').split(',')
	self.relaunch_container = []

    @debug
    def init_config(self):
        self.config = ConfigParser.RawConfigParser()
	self.config.read('/home/galadmin/etc/ispaces-client.cfg')
	self.host = self.config.get('master', 'host')
	self.port = self.config.get('master', 'port')

    @debug
    def prepare_container(self):
	for live_activity_group_name in self.relaunch_sequence:
		print "LAG: %s" % live_activity_group_name
		live_activity_group = self.master.get_live_activity_group(
				{'live_activity_group_name' : live_activity_group_name}						)
		self.relaunch_container.append(live_activity_group)
    @debug
    def loop_over_container(self):
	self.relaunched = False
	self.shutdown()
	self.status_refresh()
	self.activate()

    def shutdown(self):
	for live_activity_group in self.relaunch_container:
	    live_activity_group.send_shutdown()

    def status_refresh(self):
	for live_activity_group in self.relaunch_container:
	    live_activity_group.send_status_refresh()

    def activate(self):
	for live_activity_group in self.relaunch_container:
	    live_activity_group.send_activate()

    def relaunch(self):
        self.prepare_container()
	self.loop_over_container()

if __name__ == '__main__':
   ir = InteractiveSpacesRelaunch()
   ir.relaunch()
