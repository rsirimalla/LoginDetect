
from jsonschema import validate

from exceptions import Exception
from exception import CustomException

''' Input validation schema '''
schema = {
    "type": "object",
    "properties": {
        "username": {"type": "string"},
        "unix_timestamp": {"type": "number"},
        "event_uuid": {"type": "string"},
        "ip_address": {"type": "string"}
    },
    "required": ["username", "unix_timestamp", "event_uuid", "ip_address"]
}


def validate_payload(payload):
    ''' Validate input against payload schema '''
    try:
        validate(payload, schema)
    except Exception as e:
        raise CustomException(e.message, 400)
