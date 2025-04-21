from odoo import fields,models

class CollegeStudent(models.Model):
    _name = "college.student"
    _description = "College Student"

    name_surname = fields.Char(default= "Isim", required=True)
    age = fields.Integer(string="Yaş")