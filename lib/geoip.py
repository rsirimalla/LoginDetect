
import os
import geoip2.database
from haversine import haversine

from exception import CustomException
from exceptions import Exception


GEOIP_DATABASE = os.path.dirname(os.path.abspath(__file__)) + '/../data/GeoLite2-City.mmdb'
reader = geoip2.database.Reader(GEOIP_DATABASE)


def get_location(ip):
    '''
    Gets location details (lat, lon, accuracy_radius)

    Parameters
        ip - IP address
    Returns
        Dictionary containing lat, lon and accuracy_radius
    '''
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
    Calculate speed from one location to another location

    Logic:
    speed = distance / time

    If location is accurate (accuracy_radius =0), distance = haversine(loc1, loc2)
    If location is not accurate, i.e accurate_radius > 0
        Worst case distance (max) = haversine(loc1, loc2) + (loc1.radius + loc2.radius)
        Best  case distance (min) = haversine(loc1, loc2) - (loc1.radius + loc2.radius)             
        So the distance should be somewhere between max and min
    
    This function implements worstcase approach
    time delta = abs(payload1.unix_timestamp - payload2.unix_timestamp)
    
    Parameters:
        payload1 - source event details with ip_address, unix_timestamp (timestamp when event generated)
        payload2 - destination event details with ip_address, unix_timestamp (timestamp when event generated)
    
    Returns:
        speed in miles/hr
    '''
    try:
        loc1 = get_location(payload1['ip_address'])
        loc2 = get_location(payload2['ip_address'])

        h_distance = haversine(
            (loc1['lat'], loc1['lon']),
            (loc2['lat'], loc2['lon']),
            unit='mi'
        )

        distance = h_distance + (loc1['radius'] + loc2['radius']) * 1.6
        speed = (distance / float(abs(payload1['unix_timestamp'] - payload2['unix_timestamp']))) * 3600

        return round(speed)
    except expression as identifier:
        raise CustomException('Unable to calculate speed', 400)
