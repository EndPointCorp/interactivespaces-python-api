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

class SerializerException(Exception):
    pass

class ControllerNotFoundException(Exception):
    pass

class LiveActivityGroupNotFoundException(Exception):
    pass

class LiveActivityNotFoundException(Exception):
    pass

class ActivityNotFoundException(Exception):
    pass

class SpaceNotFoundException(Exception):
    pass
