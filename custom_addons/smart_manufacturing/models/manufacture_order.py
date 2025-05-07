from odoo import models, fields, api, _


class ManufactureOrder(models.Model):
    _name = 'smart.manufacture.order'

    _description = 'Smart Manufacture Order'
    _order = 'date_planned desc'

    name = fields.Char(string='Reference', required=True, copy=False,
                       default=lambda self: _('New'))
    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Float(string='Quantity', required=True)
    date_planned = fields.Datetime(string='Planned Date',
                                   default=fields.Datetime.now)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(self._name)
        return super(ManufactureOrder, self).create(vals_list)

    def action_plan(self):
        self.write({'state': 'planned'})

    def action_start(self):
        self.write({'state': 'in_progress'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancel'})
