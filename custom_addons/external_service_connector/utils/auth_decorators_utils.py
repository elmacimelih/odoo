# utils/auth_decorators.py
from functools import wraps
from odoo.http import request, Response
import jwt
import json
from ..dtos.api_result_dto import ApiResult
from .config_utils import get_jwt_secret


def jwt_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.httprequest.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            res = ApiResult(401, error='Missing or invalid Authorization header')
            return Response(json.dumps(res.to_dict()), status=401, content_type='application/json')

        token = auth_header.split(' ')[1]
        try:
            jwt.decode(token, get_jwt_secret(), algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            res = ApiResult(401, error='Access token expired')
            return Response(json.dumps(res.to_dict()), status=401, content_type='application/json')
        except jwt.InvalidTokenError:
            res = ApiResult(401, error='Invalid access token')
            return Response(json.dumps(res.to_dict()), status=401, content_type='application/json')

        return func(*args, **kwargs)

    return wrapper
