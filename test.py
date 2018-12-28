
from app import app
import mock
from mock import patch, Mock
import unittest
from exception import CustomException
import geoip
import validation
import json
import test_data


class LoginTests(unittest.TestCase):

    def setUp(self):
        # creates a test client
        self.app = app.test_client()
        self.app.testing = True

    def tearDown(self):
        pass

    def test_home_status_code(self):
        result = self.app.get('/')
        self.assertEqual(result.status_code, 200)

    def test_home_data(self):
        result = self.app.get('/')
        self.assertEqual(result.data, "Hello World!!!")

    def test_no_username(self):
        result = self.app.post('/v1', data=json.dumps(test_data.request_no_username), content_type='application/json')
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.data, '{"message":"\'username\' is a required property"}\n')

    def test_invalid_ip(self):
        result = self.app.post('/v1', data=json.dumps(test_data.request_invalid_ip), content_type='application/json')
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.data, '{"message":"Invalid IP or Unable to get geo location for 20600.81.252.6"}\n')

    @mock.patch('app.get_access_details')
    @mock.patch('app.geoip.get_location')
    def test_create_login(self, mock_location, mock_access_details):
        mock_location.return_value = test_data.mock_location1
        mock_access_details.return_value = {}

        result = self.app.post('/v1', data=json.dumps(test_data.request_good), content_type='application/json')        
        response = json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(response['currentGeo']['radius'], 200)
        self.assertEqual(response['travelToCurrentGeoSuspicious'], 'NA')
        self.assertEqual(response['travelFromCurrentGeoSuspicious'], 'NA')

