#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
from json_factory.response import JsonResponse
sys.path.append(os.curdir)
import unittest
import mock
import interactivespaces

ACTIVITY_DATA_HASH = JsonResponse('tests/json_factory').activity_56_initial_data_hash()
ACTIVITY_ABSOLUTE_URL = JsonResponse('tests/json_factory').activity_56_absolute_url()
ACTIVITY_URI = JsonResponse('tests/json_factory').activity_56_uri()
ACTIVITY_UPLOAD_URI = JsonResponse('tests/json_factory').activity_56_upload_uri()

class ActivityTests(unittest.TestCase):
    
    def test_unbound_activity_constructor(self):
        """ Test activity construction without URI to master API"""
        activity = interactivespaces.Activity()
        self.assertEqual(activity.class_name, 'Activity', "Activity class_name set incorrectly")
        self.assertIsInstance(activity, interactivespaces.Activity, "Activity is not an instance of Activity")
    
    def test_bound_activity_constructor(self):
        """ Test activity construction with URI to master API"""
        activity = interactivespaces.Activity(ACTIVITY_DATA_HASH, ACTIVITY_URI)
        self.assertEqual(activity.uri, ACTIVITY_URI, "Activity URI wrong")
        self.assertEqual(activity.data_hash, ACTIVITY_DATA_HASH, "Activity data hash wrong")
        self.assertEqual(activity.absolute_url, ACTIVITY_ABSOLUTE_URL, "Activity absolute url wrong")
    
    @mock.patch.object(interactivespaces.Activity, 'upload')
    def test_activity_upload_simple(self, mock_upload):
        activity = interactivespaces.Activity(ACTIVITY_DATA_HASH, ACTIVITY_URI)
        activity.upload(ACTIVITY_UPLOAD_URI, 'Mocked file handler')
        mock_upload.assert_called_with(ACTIVITY_UPLOAD_URI, 'Mocked file handler')
        
    @mock.patch.object(interactivespaces.Communicable, '_api_get_json')
    @mock.patch.object(interactivespaces.Communicable, '_api_post_json')
    def test_activity_upload_deep(self,  mock__api_post_json, mock__api_get_json):
        activity = interactivespaces.Activity(ACTIVITY_DATA_HASH, ACTIVITY_URI)
        activity.upload(ACTIVITY_URI, 'Mocked file handler')
        mock__api_post_json.assert_called_with(ACTIVITY_UPLOAD_URI, {'_eventId_save' : 'Save'}, 'Mocked file handler' )
        
if __name__ == '__main__':
    unittest.main()