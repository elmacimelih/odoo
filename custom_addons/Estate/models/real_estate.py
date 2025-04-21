from odoo import fields,models

class RealEstate(models.Model):
    _name = "real.estate"
    _description = "Test model"

    name = fields.Char(default= "House", required=True)
    price = fields.Float()