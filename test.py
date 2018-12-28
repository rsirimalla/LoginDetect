
from app import app
from mock import patch, Mock
import unittest
from exception import CustomException
import geoip
import validation
import json


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

    def test_validate_request(self):
        result = self.app.post('/v1', data=json.dumps(dict(
            unix_timestamp=1514741200,
            event_uuid="85ad929a-db03-4bf4-9541-8f728fa12e481",
            ip_address="24.242.71.20"
        )), content_type='application/json')        
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.data, '{"message":"\'username\' is a required property"}\n')
