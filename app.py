
from flask import Flask, request, jsonify, g

import sqlite3
import os
import geoip

from exceptions import Exception
from exception import CustomException
from validation import validate_payload


app = Flask(__name__)

DATABASE = os.path.join(app.root_path, 'data', 'detector.db')
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
    ''' DB resource cleaup on exit '''
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
    reader = getattr(g, '_geoipdb', None)
    if reader is not None:
        reader.close()


def get_access_details_from_db(payload, type):
    ''' Get previous/subsequent login info from DB '''
    try:
        sign = '<' if type == 'previous' else '>'
        order = 'desc' if type == 'previous' else ''

        sql = 'select ip_address, unix_timestamp, lat, lon, radius from login_geo_location where username=? and unix_timestamp {sign} ?  order by unix_timestamp {order} limit 1'
        sql = sql.format(sign=sign, order=order)
        values = [payload['username'], payload['unix_timestamp']]

        cur = get_db().execute(sql, values)
        rv = cur.fetchall()
        cur.close()

        if len(rv) == 0:
            return None

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
    ''' Insert into DB'''
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
    Get access details from previous or subsequent logins
    @payload - API payload
    @type - Login access type, permitted values => 'previous' or 'subsequent'
    '''
    try:
        response = {}

        db_result = get_access_details_from_db(payload, type)
        if db_result is None:
            return response

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
    '''POST endpoint'''
    response = {}
    try:
        validate_payload(request.json)
        response['currentGeo'] = geoip.get_location(request.json['ip_address'])
        insert_db(request.json, response['currentGeo'])
        response['precedingIpAccess'] = get_access_details(request.json, 'previous')
        response['subsequentIpAccess'] = get_access_details(request.json, 'subsequent')
        response['travelToCurrentGeoSuspicious'] = (response['precedingIpAccess']['speed'] >
                                                    SPEED_THRESHOLD) if 'speed' in response['precedingIpAccess'] else 'NA'
        response['travelFromCurrentGeoSuspicious'] = (response['subsequentIpAccess']['speed'] >
                                                      SPEED_THRESHOLD) if 'speed' in response['subsequentIpAccess'] else 'NA'
        return jsonify(response), 200
    except CustomException as e:
        return jsonify(e.to_dict()), 201
    except Exception as e:
        return jsonify({'message': 'Internal server Error'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
