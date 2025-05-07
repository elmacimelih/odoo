from .base_controller import BaseController
from odoo.http import request


class ProductController(BaseController):
    @BaseController.auth_route('/api/products', type='json', auth='none', methods=['GET'], csrf=False)
    def list(self, **kw):
        prods = request.env['product.product'].sudo().search([])
        data = [{'id': p.id, 'name': p.name, 'default_code': p.default_code, 'qty_available': p.qty_available} for p in
                prods]
        return self._make_response(data=data)

    @BaseController.auth_route('/api/products/<string:code>', type='json', auth='none', methods=['GET'], csrf=False)
    def get(self, code, **kw):
        prod = request.env['product.product'].sudo().search([('default_code', '=', code)], limit=1)
        if not prod:
            return self._make_response(error='Product not found', status_code=404)
        data = {'id': prod.id, 'name': prod.name, 'default_code': prod.default_code,
                'qty_available': prod.qty_available}
        return self._make_response(data=data)
