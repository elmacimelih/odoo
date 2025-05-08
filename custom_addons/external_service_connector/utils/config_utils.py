# utils/config_utils.py
from odoo.http import request

def get_jwt_secret():
    return request.env['ir.config_parameter'].sudo().get_param(
        'external_service_connector.jwt_secret_key'
    )
