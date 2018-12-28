
import os
import geoip2.database
from haversine import haversine

from exception import CustomException
from exceptions import Exception


GEOIP_DATABASE = os.path.dirname(os.path.abspath(__file__)) + '/data/GeoLite2-City.mmdb'
reader = geoip2.database.Reader(GEOIP_DATABASE)


def get_location(ip):
    try:
        response = {}
        location = reader.city(ip).location
        response['lat'] = location.longitude
        response['lon'] = location.latitude
        response['radius'] = location.accuracy_radius
        return response
    except Exception as e:
        print e
        raise CustomException('Invalid IP or Unable to get geo location for ' + ip, 400)


def get_speed(payload1, payload2):
    '''
    Calculate speed 

    distance = haversine distance between locations + (location1.radius + location2.radius)
    speed = distance / time delta
    '''
    try:
        loc1 = get_location(payload1['ip_address'])
        loc2 = get_location(payload2['ip_address'])

        h_distance = haversine(
            (loc1['lat'], loc1['lon']),
            (loc2['lat'], loc2['lon']),
            unit='mi'
        )

        distance = h_distance + loc1['radius'] + loc2['radius']
        speed = (distance / abs(payload1['unix_timestamp'] - payload2['unix_timestamp'])) * 3600

        return round(speed)
    except expression as identifier:
        raise CustomException('Unable to calculate speed', 400)
