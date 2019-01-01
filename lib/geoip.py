
import os
import geoip2.database
from haversine import haversine

from exception import CustomException
from exceptions import Exception


GEOIP_DATABASE = os.path.dirname(os.path.abspath(__file__)) + '/../data/GeoLite2-City.mmdb'
reader = geoip2.database.Reader(GEOIP_DATABASE)


def get_location(ip):
    '''
    Gets location details for an IP (lat, lon, accuracy_radius)

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


def get_speed(event1, event2):
    '''
    Calculate speed between two login events
    
    speed = distance / time

    If location is accurate (accuracy_radius =0), distance = haversine(loc1, loc2)
    If location is not accurate, i.e accurate_radius > 0
        Worst case(max): distance = haversine(loc1, loc2) + (loc1.radius + loc2.radius)
        Best  case(min): distance = haversine(loc1, loc2) - (loc1.radius + loc2.radius)             
        The distance should be somewhere between max and min
    
    This function implements worstcase approach
    time delta = abs(event1.unix_timestamp - event2.unix_timestamp)
    
    Parameters:
        event1 - source event details with ip_address, unix_timestamp (timestamp when event generated)
        event2 - destination event details with ip_address, unix_timestamp (timestamp when event generated)
    
    Returns:
        speed in miles/hr
    '''
    try:
        # Get location details
        loc1 = get_location(event1['ip_address'])
        loc2 = get_location(event2['ip_address'])

        # Haversine distance
        h_distance = haversine(
            (loc1['lat'], loc1['lon']),
            (loc2['lat'], loc2['lon']),
            unit='mi'
        )

        # Distance with uncertainity
        distance = h_distance + (loc1['radius'] + loc2['radius']) * 0.625

        # Speed = distance / time
        speed = (distance / float(abs(event1['unix_timestamp'] - event2['unix_timestamp']))) * 3600

        return round(speed)
    except expression as identifier:
        raise CustomException('Unable to calculate speed', 400)
