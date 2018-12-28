
request_no_username = {
    "unix_timestamp": 1514850900,
    "event_uuid": "85ad929a-db03-4bf4-9541-8f728fa12e482",
    "ip_address": "206.81.252.6"
}

request_invalid_ip = {
    "username": "axl",
    "unix_timestamp": 1514850900,
    "event_uuid": "85ad929a-db03-4bf4-9541-8f728fa12e482",
    "ip_address": "20600.81.252.6"
}

request_good = {
    "username": "axl",
    "unix_timestamp": 1514850900,
    "event_uuid": "85ad929a-db03-4bf4-9541-8f728fa12e482",
    "ip_address": "206.81.252.6"
}

mock_location1 = {
    "lat": -86.9026,
    "lon": 48.7549,
    "radius": 200
}

mock_location2 = {
    "lat": -76.9026,
    "lon": 38.7549,
    "radius": 100
}


# speed calculation test
mock_request_speed_calc = {
    "username": "axl",
    "unix_timestamp": 151480000,
    "event_uuid": "85ad929a-db03-4bf4-9541-8f728fa12e482",
    "ip_address": "2.2.2.2"
}
mock_speed_db_result = {
    'ip_address': '1.1.1.1',
    'unix_timestamp': 151483600,
    'lat': -97.7195,
    'lon': 30.4254,
    'radius': 100,
}
