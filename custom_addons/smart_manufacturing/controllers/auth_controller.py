import functools
from odoo import http
from odoo.http import request
import json
from datetime import datetime


class AuthMixin:
    @staticmethod
    def validate_token(token):
        if not token:
            return False
        key = token.split('Bearer ')[-1]
        return bool(request.env['smart.api.key']
                    .sudo()
                    .search([('key', '=', key), ('active', '=', True)], limit=1))

    @staticmethod
    def unauthorized_response(message='Unauthorized', status=401):
        body = {
            'status': 'error',
            'data': None,
            'message': message,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'path': request.httprequest.path,
            'httpStatus': status,
        }
        return http.Response(body=json.dumps(body), status=status, mimetype='application/json')

    @classmethod
    def token_required(cls, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            token = request.httprequest.headers.get('Authorization')
            if not cls.validate_token(token):
                return cls.unauthorized_response()
            return func(*args, **kwargs)

        return wrapper


class AuthController(http.Controller):
    """
    POST /api/auth/login
    Body JSON: {"db":"...","login":"...","password":"..."}
    """

    @http.route('/api/auth/login', type='json', auth='none', methods=['POST'], csrf=False)
    def login(self, db=None, login=None, password=None, **kwargs):
        if not db or not login or not password:
            return AuthMixin.unauthorized_response('db, login ve password gerekli', status=400)
        try:
            request.session.authenticate(db, login, password)
        except Exception:
            return AuthMixin.unauthorized_response('Invalid credentials', status=401)
        api_key = request.env['smart.api.key'].sudo().create({'name': login})
        body = {
            'status': 'success',
            'data': {'api_key': api_key.key},
            'message': '',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'path': request.httprequest.path,
            'httpStatus': 200,
        }
        return http.Response(body=json.dumps(body), status=200, mimetype='application/json')
