# Superman Detector

Identifies logins by a user that occur from locations that are farther apart than a normal person can reasonably travel on an airplane. These locations were determined by looking up the source IP addresses of successful logins in a GeoIP database

## Key Considerations

1. Runtime performance for IP Geolocation lookups
   - Maxmind binary database(mmdb) are highly optimized for size and performance
   - Look ups are done through a local copy of Geoip database(GeoLite2-City.mmdb)
   - The file gets loaded only once in to memory when the application starts
   - All the requests use the in-memory reader object to acheive maximum performace
2. Handling out-of-order arrival time of login events
   - Login events are stored in sqlite database.
   - Database has two timestamps.
     - Request timestamp (from the request payload)
     - Create timestamp (time when event is inserted in to DB)
   - Previous/Subsequent login events are pulled from DB based on request timesatmp (order by asc or desc)
3. Latitude and Longitude uncertainty - accuracy radius
   - Location uncertainty is expressed in the form of accuracy radius
   - if accuracy_radius = 0, distance = haversine(loc1, loc2)
   - if accuracy_radius > 0, then it can be implemnted using couple of approaches. Which approach to implement depends on bussiness requirement
     - distance(max) = haversine(loc1, loc2) + (loc1.radius + loc2.radius)
       - The upside of this approach is all the suspicious logins will be recorded. The downside is, application may record faulty suspicious logins from the same user (from same location) especially as the accuracy_radius goes higher
     - distance(min) = haversine(loc1, loc2) - (loc1.radius + loc2.radius)
       - Upside - minimal number of faulty detections. Down side - sometimes it might miss real suspicious incidents
     - Current implementation uses first approach

## Getting Started

These instructions will get you a copy of the project up and running on your local machine

### Prerequisites

- Docker
- Docker-Compose
- Python 2.7 (only for development purposes)

### Steps to run

``` bash
git clone git@github.com:rsirimalla/LoginDetect.git
cd LoginDetect
docker-compose up
```

Access the app from http://localhost:5000/v1

### Login event example

``` bash
#!/bin/bash
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"username":"demo","ip_address":"206.81.252.6", "event_uuid":"85ad929a-db03-4bf4-9541-8f728fa12e486", "unix_timestamp":151465500}' \
  http://localhost:5000/v1
```

### Running unit tests

``` bash
cd LoginDetect
pip install -r requirements.txt
python -m unittest discover tests
```

### Load testing (NodeJS vs Python)

**Scenario**: 100 concurrent requests/sec for 1 minute i.e, 6000 requests in minute

**Python**

- Request latency:
  - min: 5.1
  - max: 460
  - median: 6.5
  - p95: 9
  - p99: 27

**Node**

- Project URl: https://github.com/rsirimalla/LoginDetect-Node
- Request latency:
  - min: 1.3
  - max: 110.6
  - median: 2.1
  - p95: 2.7
  - p99: 5.1

**Observation**: Node implementation is alomost 4 times faster than Python. Its mostly because of DB connections. NodeJS can re-use same DB connection for all the requests due to its single threaded nature. Python create/destroy DB connection for every request due to its multi-threaded nature (to avoid dead locks, race conditions etc).

### Resources/External libs

- Haversine python lib - https://pypi.org/project/haversine/
- Python Flask framework - http://flask.pocoo.org/
- Payload Schema validation - https://pypi.org/project/jsonschema/
- Geoip API - https://github.com/maxmind/GeoIP2-python
- Load testing tool - https://artillery.io/