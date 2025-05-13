# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import request, Response
from werkzeug.exceptions import Unauthorized, BadRequest
from ..dtos.api_result_dto import ApiResult
from ..utils.auth_decorators_utils import jwt_required


class WorkOrderController(http.Controller):

    @http.route('/api/wo', type='http', auth='none', csrf=False, methods=['GET'])
    @jwt_required
    def get_all_workorders(self, **kwargs):
        # Limit & Offset çek
        limit_param = request.params.get('limit')
        offset_param = request.params.get('offset', 0)

        try:
            limit = int(limit_param) if limit_param is not None else None
            offset = int(offset_param)
        except ValueError:
            res = ApiResult(400, error="limit ve offset sayısal olmalıdır.")
            return Response(json.dumps(res.to_dict()), status=400, content_type='application/json')

        # Kayıtları çek
        workorders = request.env['mrp.workorder'].sudo().search([], order='production_id, id', limit=limit,
                                                                offset=offset)

        data = []
        for wo in workorders:
            mo = wo.production_id
            ops = mo.workorder_ids.sorted(key=lambda x: x.id)
            index = list(ops).index(wo)

            data.append({
                'workorder_id': wo.id,  # mrp.workorder.id → İş emrinin benzersiz ID’si
                'operation': wo.operation_id.name,  # mrp.workorder.operation_id.name → Operasyonun adı
                'state': wo.state,  # mrp.workorder.state → İş emrinin durumu (ready, progress, done, cancel)
                'workcenter': wo.workcenter_id.name,  # mrp.workorder.workcenter_id.name → İş merkezi adı
                'mo_id': mo.id,  # mrp.workorder.production_id.id → Bu iş emrinin bağlı olduğu MO ID’si
                'mo_name': mo.name,  # mrp.production.name → Üretim emri kodu (örneğin: MO00045)
                'mo_state': mo.state,  # mrp.production.state → MO’nun genel durumu
                'operation_index': index,  # Bu operasyon, MO içindeki kaçıncı sırada?
                'product': mo.product_id.display_name,  # mrp.production.product_id.display_name → Üretilecek ürün adı
                'quantity': mo.product_qty,  # mrp.production.product_qty → Üretim miktarı
                'date_planned_start': str(mo.date_start) if mo.date_start else None,
                # mrp.production.date_start → Planlanan MO başlama zamanı
                'date_start': str(wo.date_start) if wo.date_start else None,
                # mrp.workorder.date_start → Operasyonun gerçek başlangıç zamanı
                'date_finished': str(wo.date_finished) if wo.date_finished else None,
                # mrp.workorder.date_finished → Operasyonun bitiş zamanı
                'expected_duration_mins': wo.duration_expected,
                # mrp.workorder.duration_expected → Planlanan süre (dakika)
                'real_duration_mins': wo.duration,  # mrp.workorder.duration → Gerçekleşen süre (dakika)
            })

        res = ApiResult(200, payload=data)
        return Response(json.dumps(res.to_dict()), status=200, content_type='application/json')

    @http.route('/api/mo/current_workorders', type='http', auth='none', methods=['GET'], csrf=False)
    @jwt_required
    def get_current_workorders_by_mo(self, **kwargs):
        # 1. Parametre kontrolü
        mo_id_param = request.params.get('mo_id')
        if not mo_id_param:
            return Response(json.dumps(ApiResult(400, error='mo_id zorunludur').to_dict()),
                            status=400, content_type='application/json')
        try:
            mo_id = int(mo_id_param)
        except ValueError:
            return Response(json.dumps(ApiResult(400, error='mo_id tamsayı olmalıdır').to_dict()),
                            status=400, content_type='application/json')

        # 2. MO'yu getir ve var mı kontrol et
        mo = request.env['mrp.production'].sudo().browse(mo_id)
        if not mo.exists():
            return Response(json.dumps(ApiResult(404, error='Üretim emri bulunamadı').to_dict()),
                            status=404, content_type='application/json')

        # 3. İş emirlerini sırala
        workorders = mo.workorder_ids.sorted(key=lambda w: w.id)

        # 4. Progress durumundaki tüm index'leri bul
        progress_indices = [
            idx for idx, wo in enumerate(workorders)
            if wo.state == 'progress'
        ]

        if progress_indices:
            # Birden fazla progress varsa en yüksek index'e kadar al
            current_index = max(progress_indices)
        else:
            # Hiç progress yoksa, done sayısınca ilerle
            done_count = sum(1 for w in workorders if w.state == 'done')
            current_index = done_count if done_count < len(workorders) else len(workorders) - 1

        # 5. 0..current_index arasındaki tüm work order'ları al
        subset = workorders[: current_index + 1]

        # 6. Yanıt verisini hazırla
        data = []
        for wo in subset:
            idx = list(workorders).index(wo) + 1
            data.append({
                'workorder_id': wo.id,  # mrp.workorder.id
                'operation': wo.operation_id.name,  # Operasyon adı
                'state': wo.state,  # ready/progress/done
                'workcenter': wo.workcenter_id.name,  # İş merkezi adı
                'operation_index': idx,  # 0 tabanlı sıra
                'date_start': str(wo.date_start) if wo.date_start else None,
                'date_finished': str(wo.date_finished) if wo.date_finished else None,
                'expected_duration_mins': wo.duration_expected,
                'real_duration_mins': wo.duration,
            })

        return Response(json.dumps(ApiResult(200, payload=data).to_dict()),
                        status=200, content_type='application/json')

    @http.route('/api/wo/finish', type='http', auth='none', csrf=False, methods=['POST'])
    @jwt_required
    def finish_workorder_short(self, **kwargs):
        # 1) önce query parametreden oku, yoksa JSON body'den
        wo_id = request.params.get('wo_id') or kwargs.get('wo_id')
        if not wo_id:
            res = ApiResult(400, error='wo_id zorunludur')
            return Response(json.dumps(res.to_dict()), status=400, content_type='application/json')

        # 2) integer’a çevir
        try:
            wo_id = int(wo_id)
        except ValueError:
            res = ApiResult(400, error='wo_id tamsayı olmalıdır')
            return Response(json.dumps(res.to_dict()), status=400, content_type='application/json')

        # 3) iş emrini bul
        wo = request.env['mrp.workorder'].sudo().browse(wo_id)
        if not wo.exists():
            res = ApiResult(404, error='İş emri bulunamadı')
            return Response(json.dumps(res.to_dict()), status=404, content_type='application/json')

        # 4) durum kontrolü
        if wo.state != 'progress':
            res = ApiResult(409, error=f"İş emri şu an bitirilemez (Durum: {wo.state})")
            return Response(json.dumps(res.to_dict()), status=409, content_type='application/json')

        # 5) finish
        wo.button_finish()

        payload = {
            'status': 'finished',
            'workorder_id': wo.id,
            'operation': wo.operation_id.name,
            'mo': wo.production_id.name,
        }
        res = ApiResult(200, payload=payload)
        return Response(json.dumps(res.to_dict()), status=200, content_type='application/json')
