
from exceptions import Exception


class CustomException(Exception):

    def __init__(self, message, status_code):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code

    def to_dict(self):
        rv = {}
        rv['message'] = self.message
        return rv
