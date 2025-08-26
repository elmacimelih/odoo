# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import request, Response
from werkzeug.exceptions import Unauthorized, BadRequest
from ..dtos.api_result_dto import ApiResult
from ..utils.auth_decorators_utils import jwt_required


class ProductController(http.Controller):

    @http.route('/api/getAllProducts', type='http', auth='none', methods=['GET'], csrf=False)
    @jwt_required
    def get_all_products(self, **kwargs):
        try:
            limit_param = request.params.get('limit')
            offset = int(request.params.get('offset', 0))
            limit = int(limit_param) if limit_param is not None else None  # None olursa tüm ürünler gelir
        except ValueError:
            res = ApiResult(400, error='limit and offset must be integers')
            return Response(json.dumps(res.to_dict()), status=400, content_type='application/json')

        products = request.env['product.product'].sudo().search([], limit=limit, offset=offset)

        product_list = []
        for product in products:
            product_list.append({
                'id': product.id,
                'name': product.name,
                'default_code': product.default_code,
                'list_price': product.list_price,
                'qty_available': product.qty_available,
                'type': product.type,
            })

        res = ApiResult(200, payload=product_list)
        return Response(json.dumps(res.to_dict()), status=200, content_type='application/json')


    @http.route('/api/createProduct', type='json', auth='none', methods=['POST'], csrf=False)
    def create_product(self, **kwargs):

        # Hem doğrudan gelen hem de params içindeki JSON'u destekle
        params = kwargs.get('params') or kwargs

        name = params.get('name')
        default_code = params.get('default_code', '')
        list_price = params.get('list_price', 0.0)
        type_ = str(params.get('type', 'product'))  # string'e zorla

        print(name, default_code, list_price)

        # if not name:
        #     return {'error': "Ürün adı (name) zorunludur."}

        if type_ not in ['product', 'service', 'consu']:
            return {'error': f"Geçersiz type: '{type_}'. Sadece: 'product', 'service', 'consu' olabilir."}

        try:
            product_template = request.env['product.template'].sudo().create({
                'name': name,
                'default_code': default_code,
                'list_price': list_price
            })

            product = product_template.product_variant_id

            return {
                'success': True,
                'product_id': product.id,
                'name': product.name,
                'default_code': product.default_code,
                'list_price': product.list_price,
                'type': product.type,
            }

        except Exception as e:
            return {'error': str(e)}
