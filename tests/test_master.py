#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from mock import MagicMock
import json
import urllib
import urllib2
import sys
import os
sys.path.append(os.getcwd())

import interactivespaces

TEST_ACTIVITY_DATA = {
  "id":"53",
  "bundleContentHash":"hjkl",
  "identifyingName":"com.endpoint.lg.browser",
  "lastUploadDate":1398288057444,
  "description":"Browser Activity to present \"webui\" activties to the user",
  "name":"Browser Activity",
  "lastStartDate":1401901320867,
  "metadata":{},
  "version":"1.0.0.dev"
}

TEST_LIVEACTIVITY_DATA = {
  "lastDeployDate":"Mon May 05 12:50:36 PDT 2014",
  "outOfDate":False,
  "id":"110",
  "description":"",
  "name":"Evdev Demuxer on 42-a",
  "active": {
    "numberLiveActivityGroupRunning":1,
    "runtimeState":"ACTIVE",
    "deployState":"UNKNOWN",
    "lastStateUpdate":"Wed Jun 04 11:17:21 PDT 2014",
    "runtimeStateDescription":"space.activity.state.active",
    "directRunning":False,
    "directActivated":False,
    "numberLiveActivityGroupActivated":1,
    "deployStateDescription":"space.activity.state.unknown",
    "deployStateDetail":None,
    "runtimeStateDetail":"<p>foo</p>"
  },
  "controller": {
    "id":"2",
    "name":"ISCtlDispAScreen00",
    "uuid":"372f0f95-6b48-487a-a1ac-383ba580fc1c"
  },
  "uuid":"88816d20-22f6-4f78-95ba-7843696c6bc5",
  "activity": {
    "id":"61",
    "bundleContentHash":"qwerty",
    "identifyingName":"com.endpoint.lg.evdev.demuxer",
    "lastUploadDate":1398288062862,
    "description":"Separates and aggregates different types of input events.",
    "name":"Event Device Demuxer",
    "lastStartDate":1401905841864,
    "metadata":{},
    "version":"1.0.0.dev"
  },
  "metadata":{}
}

TEST_LIVEACTIVITYGROUP_DATA = {
  "id":"301",
  "description":"",
  "name":"Google Earth",
  "metadata":{}
}

TEST_SPACE_DATA = {
  "id":"401",
  "description":"",
  "name":"LG Express",
  "metadata":{}
}

TEST_CONTROLLER_DATA = {
  "state":"RUNNING",
  "hostId":"ctldispascreen00",
  "mode":"ENABLED",
  "id":"2",
  "stateDescription":"space.controller.state.running",
  "modeDescription":"space.controller.mode.enabled",
  "description":"Controller for Screen 00 on Display Node A",
  "lastStateUpdateDate":"Wed Jun 04 12:25:57 PDT 2014",
  "name":"ISCtlDispAScreen00",
  "dataBundleStateDescription":"space.controller.dataBundle.state.none",
  "uuid":"372f0f95-6b48-487a-a1ac-383ba580fc1c",
  "dataBundleState":"NO_REQUEST",
  "lastDataBundleStateUpdateDate":None,
  "metadata":{}
}

TEST_NAMEDSCRIPT_DATA = {
  "id":"3",
  "name":"foo",
  "description":"bar"
}

TEST_POST = {"foo":"bar"}
TEST_QUERY = {"zot":"zing"}
TEST_SESSION='e2s1'

TEST_HOST = '1.2.3.4'
TEST_PORT = 12345

def test_get_collection(data, method_to_test, expected_type, path_name):
  """Helper for testing collection getters."""
  master = interactivespaces.Master(TEST_HOST, TEST_PORT)
  master._api_get_json = MagicMock(return_value=[data])

  result = method_to_test(master)
  master._api_get_json.assert_called_once_with('{}/all'.format(path_name))

  return result

class MasterTests(unittest.TestCase):
  def test_constructor(self):
    """Test construction with valid arguments."""
    master = interactivespaces.Master(TEST_HOST, TEST_PORT)

    self.assertEqual(master.host, TEST_HOST)
    self.assertEqual(master.port, TEST_PORT)

  def test_api_get_json(self):
    """Test a valid call to Master._api_get_json()."""
    class MockResponse(object):
      def read():
        return '{"result":"success","data":{"foo":"bar"}}'
      def getcode():
        return 200

    master = interactivespaces.Master(TEST_HOST, TEST_PORT)
    master._urlopen = MagicMock(return_value=MockResponse())

    command = 'activity/all'
    response = master._api_get_json(command)

    master._urlopen.assert_called_once_with(
      'http://{}:{}/{}.json'.format(TEST_HOST, TEST_PORT, command)
    )
    self.assertEqual('bar', response['foo'])

  def test_api_get_html(self):
    """Test a valid call to Master._api_get_html()."""
    class MockResponse(object):
      def read():
        return 'asdf'
      def getcode():
        return 200

    master = interactivespaces.Master(TEST_HOST, TEST_PORT)
    master._urlopen = MagicMock(return_value=MockResponse())

    command = 'activity/new'
    response = master._api_get_html(command, {"foo":"bar"})

    master._urlopen.assert_called_once_with(
      'http://{}:{}/{}.html?{}'.format(
        TEST_HOST,
        TEST_PORT,
        command,
        urllib.urlencode(TEST_QUERY)
      )
    )
    self.assertEqual('asdf', response.read())
    self.assertEqual(200, response.getcode())

  def test_api_post_json(self):
    """Test a valid call to Master._api_post_json()."""
    class MockResponse(object):
      def read():
        return '{"result":"success"}'
      def getcode():
        return 200

    master = interactivespaces.Master(TEST_HOST, TEST_PORT)
    master._urlopen = MagicMock(return_value=MockResponse())

    command = 'liveactivity/42/configure'
    master._api_post_json(command, TEST_QUERY, TEST_POST)

    master._urlopen.assert_called_once_with(
      'http://{}:{}/{}.json?{}'.format(
        TEST_HOST,
        TEST_PORT,
        command,
        urllib.urlencode(TEST_QUERY)
      ),
      urllib.urlencode(TEST_POST)
    )

  def test_api_post_html(self):
    """Test a valid call to Master._api_post_html()."""
    class MockResponse(object):
      def read():
        return 'asdf'
      def getcode():
        return 200

    master = interactivespaces.Master(TEST_HOST, TEST_PORT)
    master._urlopen = MagicMock(return_value=MockResponse())

    command = 'namescript/new'
    master._api_post_html(command, TEST_QUERY, TEST_POST)

    master._urlopen.assert_called_once_with(
      'http://{}:{}/{}.html?{}'.format(
        TEST_HOST,
        TEST_PORT,
        command,
        urllib.urlencode(TEST_QUERY)
      ),
      urllib.urlencode(TEST_POST)
    )

  def test_get_all_activities(self):
    """Test Master.get_activities() with no pattern."""
    expected_type = interactivespaces.Activity
    result = test_get_collection(
      data = TEST_ACTIVITY_DATA,
      method_to_test = interactivespaces.Master.get_activities,
      expected_type = expected_type,
      path_name = 'activity'
    )
    self.assertEqual(1, len(result))
    self.assertIsInstance(result[0], expected_type)

  def test_get_live_activities(self):
    """Test Master.get_live_activities() with no pattern."""
    expected_type = interactivespaces.LiveActivity
    result = test_get_collection(
      data = TEST_LIVEACTIVITY_DATA,
      method_to_test = interactivespaces.Master.get_live_activities,
      expected_type = expected_type,
      path_name = 'liveactivity'
    )
    self.assertEqual(1, len(result))
    self.assertIsInstance(result[0], expected_type)

  def test_get_live_activity_groups(self):
    """Test Master.get_live_activity_groups() with no pattern."""
    expected_type = interactivespaces.LiveActivityGroup
    test_get_collection(
      data = TEST_LIVEACTIVITYGROUP_DATA,
      method_to_test = interactivespaces.Master.get_live_activity_groups,
      expected_type = expected_type,
      path_name = 'liveactivitygroup'
    )
    self.assertEqual(1, len(result))
    self.assertIsInstance(result[0], expected_type)

  def test_get_spaces(self):
    """Test Master.get_spaces() with no pattern."""
    expected_type = interactivespaces.Space
    test_get_collection(
      data = TEST_SPACE_DATA,
      method_to_test = interactivespaces.Master.get_spaces,
      expected_type = expected_type,
      path_name = 'space'
    )
    self.assertEqual(1, len(result))
    self.assertIsInstance(result[0], expected_type)

  def test_get_controllers(self):
    """Test Master.get_controllers() with no pattern."""
    expected_type = interactivespaces.Controller
    test_get_collection(
      data = TEST_CONTROLLER_DATA,
      method_to_test = interactivespaces.Master.get_controllers,
      expected_type = expected_type,
      path_name = 'spacecontroller'
    )
    self.assertEqual(1, len(result))
    self.assertIsInstance(result[0], expected_type)

  def test_get_named_scripts(self):
    """Test Master.get_named_scripts() with no pattern."""
    expected_type = interactivespaces.NamedScript
    test_get_collection(
      data = TEST_NAMEDSCRIPT_DATA,
      method_to_test = interactivespaces.Master.get_named_scripts,
      expected_type = expected_type,
      path_name = 'namedscript'
    )
    self.assertEqual(1, len(result))
    self.assertIsInstance(result[0], expected_type)

  def test_new_live_activity(self):
    """Test a valid call to Master.new_live_activity()."""
    master = interactivespaces.Master(TEST_HOST, TEST_PORT)

    class MockFirstResponse():
      def getcode():
        return 200
      def geturl():
        return 'http://{}:{}/liveactivity/new.html?execution={}'.format(
          TEST_HOST,
          TEST_PORT,
          TEST_SESSION
        )

    class MockSecondResponse():
      def getcode():
        return 200

    master._api_get_html  = MagicMock(return_value=MockFirstResponse())
    master._api_post_html = MagicMock(return_value=MockSecondResponse())

    class MockActivity():
      self.id = TEST_LIVEACTIVITY_DATA['activity']['id']

    class MockController():
      self.id = TEST_LIVEACTIVITY_DATA['controller']['id']

    test_live_activity = master.new_live_activity(
      TEST_LIVEACTIVITY_DATA['name'],
      TEST_LIVEACTIVITY_DATA['description'],
      MockActivity(),
      MockController()
    )
    master._api_get_html.assert_called_once_with(
      'liveactivity/new',
      {"mode": "embedded"}
    )
    master._api_post_html.assert_called_once_with(
      'liveactivity/new',
      {"execution": TEST_SESSION},
      {
        "liveActivity.name": TEST_LIVEACTIVITY_DATA['name'],
        "liveActivity.description": TEST_LIVEACTIVITY_DATA['description'],
        "activityId": TEST_LIVEACTIVITY_DATA['activity']['id'],
        "controllerId": TEST_LIVEACTIVITY_DATA['controller']['id'],
        "_eventId_save": "Save"
      }
    )

    self.assertIsInstance(
      test_live_activity,
      interactivespaces.LiveActivity
    )

def main():
  unittest.main()

if __name__=='__main__':
  main()
