from odoo.http import request


def get_base_url():
    return request.env['ir.config_parameter'].sudo().get_param(
        'external_service_connector.base_url',
        default='http://localhost:8069',
    )
