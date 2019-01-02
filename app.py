
from flask import Flask, request, jsonify, g

import sqlite3
import os
from lib import geoip

from exceptions import Exception
from lib.exception import CustomException
from lib.validation import validate_payload


app = Flask(__name__)

# sqlite db file location
DATABASE = os.path.join(app.root_path, 'data', 'detector.db')

# Superman speed threshold
SPEED_THRESHOLD = 500


def get_db():
    ''' Get DB connection object '''
    try:
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = sqlite3.connect(DATABASE)
        return db
    except Exception as e:
        print e
        raise CustomException('Unable to connect to DB', 400)


@app.teardown_appcontext
def close_connection(exception):
    ''' DB resource cleaup '''
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
    reader = getattr(g, '_geoipdb', None)
    if reader is not None:
        reader.close()


def get_access_details_from_db(payload, type):
    ''' 
    Get previous/subsequent login info from DB 

    Parameters:
        payload - Request payload
        type - "previous" or "subsequent" login event

    Returns:
        previous or subsequent databse record (if present)
        None if record not found 
    '''
    try:
        # SQL to get previous/subsequent records
        sql = 'select ip_address, unix_timestamp, lat, lon, radius from login_geo_location where username=? and unix_timestamp {sign} ?  order by unix_timestamp {order} limit 1'
        sign = '<' if type == 'previous' else '>'
        order = 'desc' if type == 'previous' else ''
        sql = sql.format(sign=sign, order=order)
        values = [payload['username'], payload['unix_timestamp']]

        # DB Cursor to fetch
        cur = get_db().execute(sql, values)
        rv = cur.fetchall()
        cur.close()

        # Return None if empty result set
        if len(rv) == 0:
            return None

        # return first record
        return {
            'ip_address': rv[0][0],
            'unix_timestamp': rv[0][1],
            'lat': rv[0][2],
            'lon': rv[0][3],
            'radius': rv[0][4],
        }
    except Exception as e:
        print e
        raise CustomException('Unable to query DB', 400)


def insert_db(payload, location):
    ''' 
    Insert into database

    Parameters:
        payload - Request payload
        location - Location details from Geoip database
    '''
    try:
        sql = 'insert into login_geo_location(username, event_uuid,ip_address, unix_timestamp, lat, lon, radius) values(?,?,?,?,?,?,?);'
        values = [payload['username'], payload['event_uuid'], payload['ip_address'],
                  payload['unix_timestamp'], location['lat'], location['lon'], location['radius']]
        get_db().execute(sql, values)
        get_db().commit()
    except Exception as e:
        print e
        raise CustomException('Unable to insert DB', 400)


def get_access_details(payload, type):
    '''
    Get access details from previous or subsequent login events

    Parameters:
        payload - Request payload
        type - Login access type, permitted values => 'previous' or 'subsequent'

    Returns:
        Previous or Subsequent event dictionary (if present)
        Empty dictionary (if event doesnt exist)
    '''
    try:
        # Init response
        response = {}

        # Get previous/susequent login event details from DB
        db_result = get_access_details_from_db(payload, type)
        if db_result is None:
            return response

        # Build response
        response['ip'] = db_result['ip_address']
        response['speed'] = geoip.get_speed(payload, db_result)
        response['lat'] = db_result['lat']
        response['lon'] = db_result['lon']
        response['radius'] = db_result['radius']
        response['timestamp'] = db_result['unix_timestamp']

        return response
    except Exception as e:
        print e
        raise CustomException('Unable to get previous/subsequent login information', 400)


@app.route('/v1', methods=['POST'])
def login():
    '''POST endpoint to detect supicious login events'''
    # Init response
    response = {}
    try:
        # Validate payload
        validate_payload(request.json)

        # Get location details (lat, lon, radius)
        response['currentGeo'] = geoip.get_location(request.json['ip_address'])

        # Insert login event into dataabse
        insert_db(request.json, response['currentGeo'])

        # get previous login event details
        response['precedingIpAccess'] = get_access_details(request.json, 'previous')

        # get subsequent login event details
        response['subsequentIpAccess'] = get_access_details(request.json, 'subsequent')

        # Set travelToCurrentGeoSuspicious flag based on speed
        # true if speed > threshold else false, 'NA' if previous login event doesnt eist
        response['travelToCurrentGeoSuspicious'] = (response['precedingIpAccess']['speed'] >
                                                    SPEED_THRESHOLD) if 'speed' in response['precedingIpAccess'] else 'NA'

        # Set travelFromCurrentGeoSuspicious flag based on speed (true if speed > threshold else false)
        # true if speed > threshold else false, 'NA' if subsequent login event doesnt eist
        response['travelFromCurrentGeoSuspicious'] = (response['subsequentIpAccess']['speed'] >
                                                      SPEED_THRESHOLD) if 'speed' in response['subsequentIpAccess'] else 'NA'
        return jsonify(response), 201
    except CustomException as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        return jsonify({'message': 'Internal server Error'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
