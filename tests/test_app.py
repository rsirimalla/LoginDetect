
from app import app
import mock
from mock import patch, Mock
import unittest
from lib.exception import CustomException
import lib.geoip as geoip
import lib.validation as validation
import json
import testdata


class LoginTests(unittest.TestCase):

    def setUp(self):
        # creates a test client
        self.app = app.test_client()
        self.app.testing = True

    def tearDown(self):
        pass

    def test_no_username(self):
        result = self.app.post('/v1', data=json.dumps(testdata.request_no_username), content_type='application/json')
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.data, '{"message":"\'username\' is a required property"}\n')

    def test_invalid_ip(self):
        result = self.app.post('/v1', data=json.dumps(testdata.request_invalid_ip), content_type='application/json')
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.data, '{"message":"Invalid IP or Unable to get geo location for 20600.81.252.6"}\n')

    @mock.patch('app.get_access_details')
    @mock.patch('app.geoip.get_location')
    @mock.patch('app.insert_db')
    def test_geo_travel_flags(self, mock_insert_db, mock_location, mock_access_details):
        mock_insert_db.return_value = True
        mock_location.return_value = testdata.mock_location1
        mock_access_details.return_value = {}

        result = self.app.post('/v1', data=json.dumps(testdata.request_good), content_type='application/json')
        response = json.loads(result.data)
        self.assertEqual(result.status_code, 201)
        self.assertEqual(response['currentGeo']['radius'], 200)
        self.assertEqual(response['travelToCurrentGeoSuspicious'], 'NA')
        self.assertEqual(response['travelFromCurrentGeoSuspicious'], 'NA')

    @mock.patch('app.geoip.haversine')
    @mock.patch('app.geoip.get_location')
    @mock.patch('app.get_access_details_from_db')
    @mock.patch('app.insert_db')
    def test_speed_calculation_suspicious(self, mock_insert_db, mock_access_details_from_db, mock_geoip_get_location, mock_haversine):
        mock_insert_db.return_value = True
        mock_access_details_from_db.return_value = testdata.mock_speed_db_result
        mock_geoip_get_location.return_value = testdata.mock_location1
        mock_haversine.return_value = 500

        result = self.app.post('/v1', data=json.dumps(testdata.mock_request_speed_calc), content_type='application/json')
        response = json.loads(result.data)
        self.assertEqual(result.status_code, 201)
        self.assertEqual(response['subsequentIpAccess']['speed'], 750)
        self.assertEqual(response['travelFromCurrentGeoSuspicious'], True)

    @mock.patch('app.geoip.haversine')
    @mock.patch('app.geoip.get_location')
    @mock.patch('app.get_access_details_from_db')
    @mock.patch('app.insert_db')
    def test_speed_calculation_not_suspicious(self, mock_insert_db, mock_access_details_from_db, mock_geoip_get_location, mock_haversine):
        mock_insert_db.return_value = True
        mock_access_details_from_db.return_value = testdata.mock_speed_db_result1
        mock_geoip_get_location.return_value = testdata.mock_location1
        mock_haversine.return_value = 500

        result = self.app.post('/v1', data=json.dumps(testdata.mock_request_speed_calc1), content_type='application/json')
        response = json.loads(result.data)
        self.assertEqual(result.status_code, 201)
        self.assertEqual(response['subsequentIpAccess']['speed'], 75)
        self.assertEqual(response['travelFromCurrentGeoSuspicious'], False)
