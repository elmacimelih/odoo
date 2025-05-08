# -*- coding: utf-8 -*-
from odoo import models, fields


class ApiRefreshToken(models.Model):
    _name = 'api.refresh_token'
    _description = 'API Refresh Token'

    token = fields.Char(required=True, index=True)
    user_login = fields.Char(required=True)
    expiry_date = fields.Datetime(required=True)
