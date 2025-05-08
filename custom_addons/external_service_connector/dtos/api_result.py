# -*- coding: utf-8 -*-
from datetime import datetime


class ApiResult:
    """
    RESTful response envelope:
    - status: HTTP status code (int)
    - requestTime: UTC ISO8601 with Z
    - payload: list of result objects
    - errorMessage: string
    """

    def __init__(self, status: int, payload=None, error: str = ''):
        self.status = status
        self.requestTime = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        self.payload = payload if payload is not None else []
        self.errorMessage = error or ''

    def to_dict(self):
        return {
            'status': self.status,
            'requestTime': self.requestTime,
            'payload': self.payload,
            'errorMessage': self.errorMessage,
        }
