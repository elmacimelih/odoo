from odoo import models, fields
import secrets


class APIKey(models.Model):
    _name = 'smart.api.key'
    _description = 'API Access Key'

    name = fields.Char(string='Key Name', required=True)
    key = fields.Char(string='API Key', required=True, copy=False,
                      default=lambda self: secrets.token_urlsafe(32))
    active = fields.Boolean(string='Active', default=True)
