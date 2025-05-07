from odoo import http
from odoo.http import request
from datetime import datetime
import json
import functools
from .auth_controller import AuthMixin


class BaseController(http.Controller, AuthMixin):
    def _make_response(self, data=None, error=None, status_code=200):
        body = {
            'status': 'error' if error else 'success',
            'data': data,
            'message': error or '',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'path': request.httprequest.path,
            'httpStatus': status_code,
        }
        return http.Response(body=json.dumps(body), status=status_code, mimetype='application/json')

    @classmethod
    def auth_route(cls, *args, **kwargs):
        def decorator(func):
            # Önce token doğrula, sonra rota oluştur
            wrapped = cls.token_required(func)
            return http.route(*args, **kwargs)(functools.wraps(func)(wrapped))

        return decorator
