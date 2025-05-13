# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import request, Response
from werkzeug.exceptions import Unauthorized, BadRequest
from ..dtos.api_result_dto import ApiResult
from ..utils.auth_decorators_utils import jwt_required


class ManufacturingController(http.Controller):

    @http.route('/api/mos', type='http', auth='none', methods=['GET'], csrf=False)
    @jwt_required
    def get_all_mos(self, **kwargs):
        # limit & offset parametrelerini al
        limit_param = request.params.get('limit')
        offset_param = request.params.get('offset', 0)
        try:
            limit = int(limit_param) if limit_param is not None else None
            offset = int(offset_param)
        except ValueError:
            res = ApiResult(400, error="limit ve offset sayısal olmalıdır.")
            return Response(json.dumps(res.to_dict()), status=400, content_type='application/json')

        # MO'ları sırayla çek
        mos = request.env['mrp.production'].sudo().search(
            [], order='id', limit=limit, offset=offset)

        data = []
        for mo in mos:
            # Tüm workorder'larını al, duruma göre say
            workorders = mo.workorder_ids.sorted(key=lambda w: w.id)
            ready_count = sum(1 for w in workorders if w.state == 'ready')
            progress_count = sum(1 for w in workorders if w.state == 'progress')
            done_count = sum(1 for w in workorders if w.state == 'done')

            data.append({
                'mo_id': mo.id,  # mrp.production.id
                'mo_name': mo.name,  # mrp.production.name
                'mo_state': mo.state,  # mrp.production.state
                'product': mo.product_id.display_name,  # mrp.production.product_id.display_name
                'quantity': mo.product_qty,  # mrp.production.product_qty
                'date_planned_start': str(mo.date_start) if mo.date_start else None,
                # mrp.production.date_start → planlanan başlangıç
                'date_finished': str(mo.date_finished) if getattr(mo, 'date_finished', False) else None,
                # mrp.production.date_finished → bitiş zamanı (varsa)
                'total_operations': len(workorders),  # Toplam iş emri sayısı
                'ready_operations': ready_count,  # Hazır (ready) durumundaki operasyonlar
                'in_progress_operations': progress_count,  # Başlanmış operasyonlar
                'completed_operations': done_count,  # Tamamlanmış operasyonlar
            })

        res = ApiResult(200, payload=data)
        return Response(json.dumps(res.to_dict()), status=200, content_type='application/json')
