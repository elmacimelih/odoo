from .base_controller import BaseController
from odoo.http import request


class StockController(BaseController):
    @BaseController.auth_route('/api/stock', type='json', auth='none', methods=['GET'], csrf=False)
    def list(self, **kw):
        quants = request.env['stock.quant'].sudo().search([])
        data = [{'product_id': q.product_id.id, 'location': q.location_id.id, 'quantity': q.quantity} for q in quants]
        return self._make_response(data=data)

    @BaseController.auth_route('/api/stock', type='json', auth='none', methods=['POST'], csrf=False)
    def update(self, product_id=None, default_code=None, quantity=None, **kw):
        if quantity is None:
            return self._make_response(error='quantity required', status_code=400)
        pm = request.env['product.product'].sudo()
        prod = pm.browse(int(product_id)) if product_id else pm.search([('default_code', '=', default_code)], limit=1)
        if not prod:
            return self._make_response(error='Product not found', status_code=404)
        quants = request.env['stock.quant'].sudo().search([('product_id', '=', prod.id)])
        quants.write({'quantity': float(quantity)})
        return self._make_response(data={'updated': len(quants)})
