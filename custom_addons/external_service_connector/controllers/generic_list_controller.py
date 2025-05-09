from odoo import http
from odoo.http import request, Response
import json
from ..dtos.api_result_dto import ApiResult
from ..enums.model_map import MODEL_MAP
from ..utils.auth_decorators_utils import jwt_required


class GenericListController(http.Controller):

    @http.route('/api/getList', type='http', auth='none', methods=['GET'], csrf=False)
    @jwt_required
    def get_list(self, **kwargs):
        model_type = request.params.get('type')
        limit_param = request.params.get('limit')
        offset_param = request.params.get('offset', 0)

        try:
            limit = int(limit_param) if limit_param is not None else None  # None = tüm kayıtlar
            offset = int(offset_param)
        except ValueError:
            res = ApiResult(400, error="limit ve offset sayısal olmalıdır.")
            return Response(json.dumps(res.to_dict()), status=400, content_type='application/json')

        if not model_type or model_type not in MODEL_MAP:
            res = ApiResult(400, error=f"Geçersiz 'type'. Desteklenenler: {list(MODEL_MAP.keys())}")
            return Response(json.dumps(res.to_dict()), status=400, content_type='application/json')

        model_name = MODEL_MAP[model_type]
        try:
            records = request.env[model_name].sudo().search([], limit=limit, offset=offset)
            result = [{'id': r.id, 'value': r.display_name} for r in records]
            res = ApiResult(200, payload=result)
            return Response(json.dumps(res.to_dict()), status=200, content_type='application/json')
        except Exception as e:
            res = ApiResult(400, error=str(e))
            return Response(json.dumps(res.to_dict()), status=400, content_type='application/json')
