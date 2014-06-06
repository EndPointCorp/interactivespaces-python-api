#!/usr/bin/env python
# -*- coding: utf-8 -*-

class MasterException(Exception):
    pass

class PathException(Exception):
    pass

class CommunicableException(Exception):
    pass

class LiveActivityException(Exception):
    pass

class StatusableException(Exception):
    pass

class ActivityException(Exception):
    pass