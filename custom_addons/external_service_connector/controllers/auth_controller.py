# -*- coding: utf-8 -*-
import json, datetime, jwt, logging, hashlib, os
from odoo import http, _
from odoo.http import request, Response
from werkzeug.exceptions import Unauthorized
from ..dtos.api_result import ApiResult

_logger = logging.getLogger(__name__)

JWT_SECRET_PARAM = 'external_service_connector.jwt_secret_key'
LOGIN_USER_PARAM = 'external_service_connector.login_user'
LOGIN_PASS_PARAM = 'external_service_connector.login_password'

ACCESS_TOKEN_EXPIRY_HOURS = 10
REFRESH_TOKEN_EXPIRY_DAYS = 7


def _get_jwt_secret():
    secret = request.env['ir.config_parameter'].sudo().get_param(JWT_SECRET_PARAM)
    if not secret:
        raise Unauthorized(_('JWT secret is not configured.'))
    return secret


def generate_refresh_token():
    random_bytes = os.urandom(64)
    return hashlib.sha256(random_bytes).hexdigest()


class AuthController(http.Controller):

    @http.route('/api/login', type='http', auth='none', methods=['POST'], csrf=False)
    def login(self, **kwargs):
        try:
            body = json.loads(request.httprequest.data.decode())
            username  = body.get('username')
            password = body.get('password')
        except Exception:
            res = ApiResult(400, error='Invalid JSON')
            return Response(json.dumps(res.to_dict()), status=400, content_type='application/json')

        params = request.env['ir.config_parameter'].sudo()
        exp_username = params.get_param(LOGIN_USER_PARAM)
        exp_pass = params.get_param(LOGIN_PASS_PARAM)

        if username != exp_username or password != exp_pass:
            res = ApiResult(401, error='Invalid credentials')
            return Response(json.dumps(res.to_dict()), status=401, content_type='application/json')

        access_exp = datetime.datetime.utcnow() + datetime.timedelta(hours=ACCESS_TOKEN_EXPIRY_HOURS)
        refresh_exp = datetime.datetime.utcnow() + datetime.timedelta(days=REFRESH_TOKEN_EXPIRY_DAYS)

        access_token = jwt.encode({'username': username, 'exp': access_exp}, _get_jwt_secret(), algorithm='HS256')
        refresh_token = generate_refresh_token()

        # Save refresh token to database
        request.env['api.refresh_token'].sudo().create({
            'token': refresh_token,
            'user_login': username,
            'expiry_date': refresh_exp
        })

        payload = [{
            'access_token': access_token,
            'access_token_expiry': access_exp.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'refresh_token': refresh_token,
            'refresh_token_expiry': refresh_exp.strftime('%Y-%m-%dT%H:%M:%SZ'),
        }]
        res = ApiResult(200, payload=payload)
        return Response(json.dumps(res.to_dict()), status=200, content_type='application/json')

    @http.route('/api/refresh-token', type='http', auth='none', methods=['POST'], csrf=False)
    def refresh_access_token(self, **kwargs):
        try:
            body = json.loads(request.httprequest.data.decode())
            refresh_token = body.get('refresh_token')
        except Exception:
            res = ApiResult(400, error='Invalid JSON')
            return Response(json.dumps(res.to_dict()), status=400, content_type='application/json')

        token_record = request.env['api.refresh_token'].sudo().search([
            ('token', '=', refresh_token),
            ('expiry_date', '>', datetime.datetime.utcnow())
        ], limit=1)

        if not token_record:
            res = ApiResult(401, error='Invalid or expired refresh token')
            return Response(json.dumps(res.to_dict()), status=401, content_type='application/json')

        access_exp = datetime.datetime.utcnow() + datetime.timedelta(hours=ACCESS_TOKEN_EXPIRY_HOURS)
        new_access_token = jwt.encode(
            {'username': token_record.user_login, 'exp': access_exp},
            _get_jwt_secret(),
            algorithm='HS256'
        )

        payload = [{
            'access_token': new_access_token,
            'access_token_expiry': access_exp.strftime('%Y-%m-%dT%H:%M:%SZ'),
        }]
        res = ApiResult(200, payload=payload)
        return Response(json.dumps(res.to_dict()), status=200, content_type='application/json')
