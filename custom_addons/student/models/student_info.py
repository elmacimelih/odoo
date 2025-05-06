# -*- coding: utf-8 -*-
from email.policy import default
from re import search


from odoo import api, models, fields
from odoo.exceptions import UserError
import time
from lxml import etree
import logging
from odoo.fields import Command

from odoo.fields import Datetime
from odoo.tools import conditional

_logger = logging.getLogger("Custom Logger")

class partner(models.Model):
    _inherit = "res.partner"

    # @api.model_create_multi
    # def create(self, vals):
    #     print(self, vals)
    #     return super(partner, self).create(vals)
    #
    # def write(self, vals):
    #     print(self, vals)
    #     return super(partner, self).write(vals)

class sale(models.Model):
    _inherit = "sale.order"

    # @api.model_create_multi
    # def create(self, vals):
    #     print(self, vals)
    #     return super(sale, self).create(vals)

    # def write(self, vals):
    #     print(self, vals)
    #     return super(sale, self).write(vals)


class saleline(models.Model):
    _inherit = "sale.order.line"

    # def unlink(self):
    #     print(self)
    #     return super(saleline, self).unlink()

    # @api.model_create_multi
    # def create(self, vals):
    #     print(self, vals)
    #     return super(saleline, self).create(vals)

    # def write(self, vals):
    #     print(self, vals)
    #     return super(saleline, self).write(vals)

class DummyStudentClass(models.Model):
    _name = "dummy.student.model"
    _table = "my_abc_student"
    _description = "This is demo student model profile"

class DummyStudent(models.Model):
    _name = "dummy.student"
    _table = "my_dummy_student"
    _description = "This is demo student profile"

class DemoSchool(models.Model):
    _name = "demo.school"
    _description = "This is demo profile"

    name = fields.Char("test")


class School(models.Model):
    _name="wb.school"
    _description = "This is school profile."

    active = fields.Boolean("Archive / Soft Remove / Remove Filter", default = True) #soft delete anlamina gelir. Unarchive yapilinca dbdeki active alani true olarak degisir

#Odoo'nun çekirdeğinde Many2one alanlar, bir kayıt gösterileceğinde name_get() fonksiyonunu otomatik olarak çağırır. Bu fonksiyonun varsayılan davranışı, ilgili modelde name alanı varsa onu göstermektir. Yani:
#Eğer name dışındaki bir alanı göstermek istiyorsan ve ismini değiştirmek istemiyorsan, name_get() metodunu override ederek şu şekilde yapabilirsin:
# class School(models.Model):
#     _name = "wb.school"
#     _description = "This is school profile."
#
#     school_name = fields.Char("School Name", required=True)
#
#     def name_get(self):
#         return [(rec.id, rec.school_name) for rec in self]

    school_image = fields.Image("School Image", max_width=128, max_height=128)

    invoice_id=fields.Many2one("account.move")

    #invoice_user_id = fields.Many2one("res.users", related="invoice_id.invoice_user_id")

    invoice_incoterm_id = fields.Many2one(comodel_name="account.incoterms", related="invoice_id.invoice_incoterm_id", string="Incoterm Module", store=True)
    invoice_date = fields.Date(related="invoice_id.invoice_date")
    # invoice_total_amount = fields.Monetary(related="invoice_id.amount_residual")

    #currency_id = fields.Many2one("res.currency", related="invoice_id.currency_id")

    my_currency_id = fields.Many2one("res.currency", string="My Currency")
    #currency_id = fields.Many2one("res.currency")
    amount = fields.Monetary("Amount", currency_field="my_currency_id", default=0)


    invoice_total_amount = fields.Monetary(related="invoice_id.amount_residual", currency_field="my_currency_id", store=True)


    ref_field_id = fields.Reference(selection=[
        ('wb.school','School'),
        ('wb.student','Student'),
        ('wb.hobby','Hobby'),
        ('sale.order', 'Sale'),

    ])

    binary_field = fields.Binary()
    binary_field_name = fields.Char("Binary File Name")
    binary_fields = fields.Many2many(comodel_name="ir.attachment", string="Multi Files")



    name = fields.Char("School Name", required=True)
    student_list = fields.One2many("wb.student","school_id")

    #@api.model
    #@api.model_create_single
    @api.model_create_multi
    def create(self, vals):
        print(vals)
        rtn = super(School, self).create(vals)
        print(rtn)
        return rtn

    def write(self, vals):
        print("Write Method Called!")
        print(self)
        print(vals)
        rtn = super(School, self).write(vals)
        print(rtn)
        return  rtn

    #| Komut           | Açıklama                                            |
    # | --------------- | --------------------------------------------------- |
    # | `(0, 0, vals)`  | Yeni bir kayıt oluşturur                            |
    # | `(1, id, vals)` | Mevcut bir kaydı günceller                          |
    # | `(2, id, 0)`    | Mevcut bir kaydı siler                              |
    # | `(3, id, 0)`    | Many2many ilişkisinden çıkarır (kaydı silmez)       |
    # | `(4, id, 0)`    | Many2many ilişkisine **ekler** (varsa tekrar etmez) |
    # | `(5, 0, 0)`     | Tüm ilişkileri sıfırlar (Many2many)                 |
    # | `(6, 0, [ids])` | Many2many ilişkisini tamamen **yeniden tanımlar**   |



    def custom_method(self):

        partner = self.env['res.partner'].browse(3)
        print(partner, self)

        partner.write({'category_id':[Command.clear()]})


        # partner = self.env['res.partner'].browse(3)
        # print(partner, self)
        #
        # partner.write({
        #     "category_id":[
        #         Command.link(1)
        #     ]
        # })

        # partner = self.env['res.partner'].browse(3)
        # print(partner, self)
        #
        # partner.write({
        #     "category_id":[
        #         Command.unlink(1)
        #     ]
        # })

        #{'category_id': [[4, 1], [4, 2]], 'parent_id': 8, 'company_id': False}

        #
        # sale = self.env['sale.order'].browse(8)
        # # print(sale)
        #
        # sale.write({
        #     "order_line":[
        #         Command.delete(12)
        #     ]
        # })
        #

        #write icin
        # sale = self.env['sale.order'].browse(8)
        # print(sale)
        #
        # sale.write({
        #     "order_line": [
        #         (1, 10, {"price_unit": 100}),
        #         (1, 11, {"price_unit": 120}),
        #         (1, 12, {"price_unit": 140})
        #     ]
        # })

        #create icin
        # sale_order_vals = {'locked': False, 'partner_id': 1, 'validity_date': '2025-06-04', 'date_order': '2025-05-05 11:09:25',
        #   'show_update_pricelist': False, 'pricelist_id': 1, 'company_id': 1, 'payment_term_id': False, 'order_line': [
        #         Command.create({'sequence': 10, 'display_type': False, 'is_downpayment': False, 'product_id': 1,
        #                             'product_template_id': 1, 'product_custom_attribute_value_ids': [],
        #                             'product_no_variant_attribute_value_ids': [], 'linked_line_id': False,
        #                             'virtual_id': False, 'linked_virtual_id': False, 'selected_combo_items': False,
        #                             'combo_item_id': False, 'name': 'Computer', 'product_uom_qty': 1, 'move_ids': [],
        #                             'product_uom': 1, 'customer_lead': 0, 'price_unit': 1, 'technical_price_unit': 1,
        #                             'tax_id': [[4, 31]], 'product_document_ids': [], 'invoice_lines': []}
        #                         ),
        #
        #         Command.create({'sequence': 10, 'display_type': False, 'is_downpayment': False, 'product_id': 1,
        #                         'product_template_id': 1, 'product_custom_attribute_value_ids': [],
        #                         'product_no_variant_attribute_value_ids': [], 'linked_line_id': False,
        #                         'virtual_id': False, 'linked_virtual_id': False, 'selected_combo_items': False,
        #                         'combo_item_id': False, 'name': 'Computer', 'product_uom_qty': 1, 'move_ids': [],
        #                         'product_uom': 1, 'customer_lead': 0, 'price_unit': 2, 'technical_price_unit': 1,
        #                         'tax_id': [[4, 31]], 'product_document_ids': [], 'invoice_lines': []}
        #                        ),
        #
        #         Command.create({'sequence': 10, 'display_type': False, 'is_downpayment': False, 'product_id': 1,
        #                         'product_template_id': 1, 'product_custom_attribute_value_ids': [],
        #                         'product_no_variant_attribute_value_ids': [], 'linked_line_id': False,
        #                         'virtual_id': False, 'linked_virtual_id': False, 'selected_combo_items': False,
        #                         'combo_item_id': False, 'name': 'Computer', 'product_uom_qty': 1, 'move_ids': [],
        #                         'product_uom': 1, 'customer_lead': 0, 'price_unit': 3, 'technical_price_unit': 1,
        #                         'tax_id': [[4, 31]], 'product_document_ids': [], 'invoice_lines': []}
        #                        ),
        #     ],
        #   'note': False, 'sale_order_option_ids': [], 'quotation_document_ids': [],
        #   'customizable_pdf_form_fields': False, 'user_id': 2, 'team_id': 1, 'require_signature': True,
        #   'require_payment': False, 'prepayment_percent': 1, 'client_order_ref': False, 'tag_ids': [],
        #   'show_update_fpos': False, 'fiscal_position_id': False, 'partner_invoice_id': 1, 'journal_id': False,
        #   'warehouse_id': 1, 'incoterm': False, 'incoterm_location': False, 'picking_policy': 'direct',
        #   'commitment_date': False, 'origin': False, 'opportunity_id': False, 'campaign_id': False, 'medium_id': False,
        #   'source_id': False, 'signed_by': False, 'signed_on': False, 'signature': False}
        #
        # so = self.env["sale.order"].create(sale_order_vals)
        # print(so, so.name)

        # schools = self.search([('active', '=', False)])
        # print(schools, len(schools))

        # _logger.info("This is the Info Log")
        # _logger.debug("This is the debug Log")
        # _logger.error("This is the error Log")
        # _logger.critical("This is the critical Log")
        # _logger.warning("This is the warning Log")

        # print("Custom Method Executed!")
        # print(self)
        #
        # abc = self.env["wb.student"].search([])
        # print(abc.read(fields=["name", "school_id"]))
        # print(abc)
        # print(self.read())

        return
        # print(self.search([], order="name"))
        # print(self.search([], order="id desc"))
        #
        # #limit kaç tane kayıt gönderilecek, offset kaçıncı kayıttan başlanacak,
        # print(self.search([], limit=5, offset=0))
        # print(self.env["wb.student"].search([("name", "ilike", "test"),("name", "ilike", "ODTÜ")]))
        # print(self.search([("name", "ilike", "ODTÜ")]))

        # print(self)
        # self.write({"name":"Write Update", "amount":40})
        # pass
        # print("Clicked!")
        # data = [
        #     {"name":"Melih Record 1"},
        #     {"name": "Melih Record 2"},
        #     {"name": "Melih Record 3"},
        #     {"name": "Melih Record 4"},
        #     {"name": "Melih Record 5"},
        # ]
        # self.env["wb.school"].create(data)

        # amount = 1000

        # records = self.search([("amount",">",10)])
        # records = self.search([("amount","=",0)])
        # records = self.search([("amount","=?",None)])
        # records = self.search([("amount","=", None)])

        # records = self.search([("name","in", ("MIT", "Hello"))])
        # records = self.search([("name","not in", ("MIT", "Hello"))])
        # self.print_table(records)

        records = self.env["stock.location"].search([("id", "child_of", "1")])
        records = self.env["stock.location"].search([("id", "parent_of", "1")])

        self.print_table(records)

        return
        records = self.search([("name","=","oDTÜ")])
        self.print_table(records)

        records = self.search([("name","=","ODTÜ")])
        self.print_table(records)


    def print_table(self, records):
        print(f"Total Record Found :- {len(records)}")
        print("ID                       Name                         Amount")
        for rec in records:
            # print(f"{rec.id}                   {rec.name}                        {rec.amount}")
              print(f"{rec.id}             {rec.name}        {rec.parent_id.name} / {rec.parent_id.id}")
        print("")
        print("")

    # @api.model
    # def get_view(self, view_id=None, view_type="form", **options):
    #     # print("Test1")
    #     rtn = super(School, self).get_view(view_id=view_id, view_type=view_type, **options)
    #     # print(rtn,"test2")
    #     if view_type == "form" and "arch" in rtn:
    #         print(self, view_id, view_type, options)
    #         doc =etree.fromstring(rtn["arch"])
    #         school_field = etree.Element("field", {"name":"student_id"})
    #         targeted_field =doc.xpath("//field[@name='name']")
    #         if targeted_field:
    #             targeted_field[0].addnext(school_field)
    #         rtn['arch'] = etree.tostring(doc, encoding="inicode")
    #         print(rtn)
    #     return rtn


class Student(models.Model):
    _name = 'wb.student'
    _description = 'This is student profile.'

    #name = fields.Char("Name", unaccent=False)
    #name1 = fields.Char("Name1", translate=True, tracking=True) #tracking değişiklik yapıldığında logda tutulup tutulmayacağını belirtir. Formun en sonunda
    #name2 = fields.Char("Name2", copy=False)
    #name3 = fields.Char("Name3", default="Melih")
    #name4 = fields.Char("Name4", readonly=True)
    #student_name = fields.Char(string="Student", required=True, index=True)

    hobby_list=fields.Many2many("wb.hobby","student_hobby_list_relation","student_id","hobby_id")
    hobby_list_ids=fields.Many2many("wb.hobby",string="Hobbies", help="Select a hobby")

    school_id = fields.Many2one(comodel_name="wb.school", string="Select School")

    joining_datetime = fields.Datetime(default=Datetime.now())
    #joining_date = fields.Date(default=fields.date.today())
    joining_date = fields.Date(default=fields.Date.context_today)
    start_date = fields.Date(default=time.strftime("%Y-01-01"))
    end_date = fields.Date(default=time.strftime("%Y-12-31"))

    school_data = fields.Json()

    @api.model
    def _get_vip_list(self):
        return [('a','1'),('b','2'),('c','3')]

    #student_fees = fields.Float(digits="Payment Terms") ayarlardan currency digit adini buraya kopyalamak yeterlidir
    student_fees = fields.Float(default=3.2)
    discount_fees = fields.Float(string="Discount")

    roll_number = fields.Integer()

    gender = fields.Selection(
        [('male','Male'),('female','Female')]
    )#must be string key is id, value is text
    advance_gender = fields.Selection("_get_advance_gender_list", help="Please select a gender")
    vip_gender = fields.Selection("_get_vip_list", "VIP Gen")
    combobox = fields.Selection(selection=[('male','Male'),('female','Female')],string = "Combo Box")


    is_default_demo = fields.Boolean(default=True)
    is_paid = fields.Boolean(help="This fields is for the student paid or not the full fees!", default=True)
    name = fields.Char("Name")
    name1 = fields.Char("Name1")
    name2 = fields.Char("Name2")
    name3 = fields.Char("Name3")
    name4 = fields.Char("Name4")

    student_name = fields.Char("STD", size=5)
    address = fields.Text(string="Student Address", help="Enter here to add student address", default="Hello student address") #help=tooltip
    address_html = fields.Html(string="Address HTML",
                               #required=True,
                               #default="<h1>This is default value from backend</h1>",
                               readonly=False, copy=False,
                               help="This field uses for the dynamic html code to render into the student profile.")

    compute_address_html = fields.Html(string="Compute HTML")

    @api.onchange("address_html")
    def _onchange_address(self):
        for record in self:
            record.compute_address_html = record.address_html

    final_fees = fields.Float(string="Final Fees", compute="_compute_final_fees_cal", store=True)

    @api.onchange("student_fees", "discount_fees")
    def _compute_final_fees_cal(self):
        for record in self:
            record.final_fees = record.student_fees - record.discount_fees


    def _get_advance_gender_list(self):
        return [('male','Male'),('female','Female')]


    def json_data_store(self):
        self.school_data = {"name":self.name, "id":self.id, "fees":self.student_fees, "g":self.vip_gender}

    def custom_method(self):
        print("Custom Method Executed!")


        #
        # print(self)
        # self.write({"name":"Write Update", "amount":40})
        # pass
        # print("Clicked!")
        # data = [
        #     {"name":"Melih Record 1"},
        #     {"name": "Melih Record 2"},
        #     {"name": "Melih Record 3"},
        #     {"name": "Melih Record 4"},
        #     {"name": "Melih Record 5"},
        # ]
        # self.env["wb.school"].create(data)

    def duplicate_records(self):
        # print(self)
        duplicate_record = self.copy({"joining_date":fields.Datetime.now()})
        # print(duplicate_record)

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        print(self)
        print(default)
        rtn = super(Student, self).copy(default=default)
        print(rtn)
        return rtn

    def delete_records(self):
        print(self)
        school_id = self.env["wb.school"].browse(263)
        for school in school_id:
            if not school.exists():
                raise UserError(f"Recordset is not available! {school}")
                print("Instance or Recordset is not available", school)
            else:
                print("Instance or Recordset is available", school)
        # print(school_id)
        # print(school_id.unlink())



class Hobby(models.Model):
    _name="wb.hobby"
    _description = "This is student hobbies"

    name = fields.Char(string="Hobby Name")
