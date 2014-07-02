#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
sys.path.append(os.curdir)
import unittest
import interactivespaces
import logging

TEST_HOST = "lg-head"
TEST_PORT = "8080"
TEST_PREFIX = "/interactivespaces"

class MasterTests(unittest.TestCase):
    def test_constructor(self):
        """Test construction with valid arguments."""
        master = interactivespaces.Master(TEST_HOST, TEST_PORT, TEST_PREFIX)
        self.assertEqual(master.host, TEST_HOST, "Master host not set correctly")
        self.assertEqual(master.port, TEST_PORT, "Master port not set correctly")
        self.assertEqual(master.prefix, TEST_PREFIX, "Master prefix not set correctly")
        self.assertIsInstance(master.log, logging.Logger, "Logger is not an instance of logging.Logger")
        self.assertIsInstance(master, interactivespaces.Master, "Master is not an instance of Master")
        
    def test_api_get_json(self):
        """Test a valid call to Master._api_get_json()."""
        
if __name__ == '__main__':
    unittest.main()
  
"""
def test_get_collection(data, method_to_test, expected_type, path_name):
    master = interactivespaces.Master(TEST_HOST, TEST_PORT)
    master._api_get_json = MagicMock(return_value=[data])

    result = method_to_test(master)
    master._api_get_json.assert_called_once_with('{}/all'.format(path_name))

    return result
    
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


class MockResponse2(object):
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

        expected_type = interactivespaces.Activity
        result = test_get_collection(
                                     data=TEST_ACTIVITY_DATA,
                                     method_to_test=interactivespaces.Master.get_activities,
                                     expected_type=expected_type,
                                     path_name='activity'
                                     )
        self.assertEqual(1, len(result))
        self.assertIsInstance(result[0], expected_type)

    def test_get_live_activities(self):
        expected_type = interactivespaces.LiveActivity
        result = test_get_collection(
                                     data=TEST_LIVEACTIVITY_DATA,
                                     method_to_test=interactivespaces.Master.get_live_activities,
                                     expected_type=expected_type,
                                     path_name='liveactivity'
                                     )
        self.assertEqual(1, len(result))
        self.assertIsInstance(result[0], expected_type)

    def test_get_live_activity_groups(self):

        expected_type = interactivespaces.LiveActivityGroup
        test_get_collection(
                            data=TEST_LIVEACTIVITYGROUP_DATA,
                            method_to_test=interactivespaces.Master.get_live_activity_groups,
                            expected_type=expected_type,
                            path_name='liveactivitygroup'
                            )
        self.assertEqual(1, len(result))
        self.assertIsInstance(result[0], expected_type)

    def test_get_spaces(self):
        expected_type = interactivespaces.Space
        test_get_collection(
                            data=TEST_SPACE_DATA,
                            method_to_test=interactivespaces.Master.get_spaces,
                            expected_type=expected_type,
                            path_name='space'
                            )
        self.assertEqual(1, len(result))
        self.assertIsInstance(result[0], expected_type)

    def test_get_controllers(self):
        expected_type = interactivespaces.Controller
        test_get_collection(
                            data=TEST_CONTROLLER_DATA,
                            method_to_test=interactivespaces.Master.get_controllers,
                            expected_type=expected_type,
                            ath_name='spacecontroller'
                            )
        self.assertEqual(1, len(result))
        self.assertIsInstance(result[0], expected_type)

    def test_get_named_scripts(self):
        expected_type = interactivespaces.NamedScript
        test_get_collection(
                            data=TEST_NAMEDSCRIPT_DATA,
                            method_to_test=interactivespaces.Master.get_named_scripts,
                                expected_type=expected_type,
                                path_name='namedscript'
                                )
        self.assertEqual(1, len(result))
        self.assertIsInstance(result[0], expected_type)

    def test_new_live_activity(self):
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

    master._api_get_html = MagicMock(return_value=MockFirstResponse())
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

if __name__ == '__main__':
  main()
  
  """
