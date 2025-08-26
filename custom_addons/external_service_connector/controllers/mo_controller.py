# -*- coding: utf-8 -*-
import json
import logging
from odoo import http
from odoo.http import request, Response
from werkzeug.exceptions import Unauthorized, BadRequest
from ..dtos.api_result_dto import ApiResult
from ..utils.auth_decorators_utils import jwt_required


class ManufacturingController(http.Controller):

    @http.route('/api/manufacturing-orders', type='http', auth='none', methods=['GET'], csrf=False)
    @jwt_required
    def get_manufacturing_orders(self, **kwargs):
        try:
            # limit & offset parametrelerini al
            limit_param = request.params.get('limit')
            offset_param = request.params.get('offset', 0)
            
            try:
                limit = int(limit_param) if limit_param is not None else None
                offset = int(offset_param)
            except ValueError:
                res = ApiResult(400, error="limit ve offset sayısal olmalıdır.")
                return Response(json.dumps(res.to_dict()), status=400, content_type='application/json')

            # Get superuser environment
            env = request.env(user=1)

            # MO'ları sırayla çek
            mos = env['mrp.production'].search([], order='id', limit=limit, offset=offset)

            data = []
            for mo in mos:
                try:
                    # Work orders basic bilgileri - only safe fields
                    workorders = []
                    for wo in mo.workorder_ids.sorted(key=lambda w: w.id):
                        wo_data = {
                            'wo_id': wo.id,
                            'wo_name': wo.name,
                            'wo_state': wo.state,
                        }

                        # Only add fields that definitely exist
                        if hasattr(wo, 'operation_id') and wo.operation_id:
                            wo_data['operation_id'] = wo.operation_id.id
                            wo_data['operation_name'] = wo.operation_id.name
                        else:
                            wo_data['operation_id'] = None
                            wo_data['operation_name'] = None

                        if hasattr(wo, 'workcenter_id') and wo.workcenter_id:
                            wo_data['workcenter_id'] = wo.workcenter_id.id
                            wo_data['workcenter_name'] = wo.workcenter_id.name
                        else:
                            wo_data['workcenter_id'] = None
                            wo_data['workcenter_name'] = None

                        # Add duration information
                        wo_data['duration_expected'] = getattr(wo, 'duration_expected', 0)
                        wo_data['duration_actual'] = getattr(wo, 'duration', 0)
                        wo_data['duration_difference'] = wo_data['duration_actual'] - wo_data['duration_expected'] if \
                        wo_data['duration_expected'] > 0 else 0

                        # Add quantity information
                        wo_data['qty_production'] = getattr(wo, 'qty_production', 0)
                        wo_data['qty_produced'] = getattr(wo, 'qty_produced', 0)
                        wo_data['qty_remaining'] = getattr(wo, 'qty_remaining', 0)

                        workorders.append(wo_data)

                    # Work order durumları sayısı
                    ready_count = sum(1 for w in mo.workorder_ids if w.state == 'ready')
                    progress_count = sum(1 for w in mo.workorder_ids if w.state == 'progress')
                    done_count = sum(1 for w in mo.workorder_ids if w.state == 'done')
                    waiting_count = sum(1 for w in mo.workorder_ids if w.state == 'pending')
                    cancel_count = sum(1 for w in mo.workorder_ids if w.state == 'cancel')

                    # Build MO data safely
                    mo_data = {
                        'mo_id': mo.id,
                        'mo_name': mo.name,
                        'mo_state': mo.state,
                        'product_id': mo.product_id.id if mo.product_id else None,
                        'product_code': mo.product_id.default_code if mo.product_id else None,
                        'product_name': mo.product_id.display_name if mo.product_id else None,
                        'product_qty': mo.product_qty,
                        'qty_produced': getattr(mo, 'qty_produced', 0),
                        'create_date': str(mo.create_date),
                        'write_date': str(mo.write_date),

                        # Work Order Counts
                        'total_workorders': len(mo.workorder_ids),
                        'waiting_workorders': waiting_count,
                        'ready_workorders': ready_count,
                        'in_progress_workorders': progress_count,
                        'done_workorders': done_count,
                        'cancelled_workorders': cancel_count,

                        # Detailed Work Orders
                        'workorders': workorders,

                        # Progress Calculation
                        'progress_percentage': round((done_count / len(mo.workorder_ids) * 100), 2) if len(
                            mo.workorder_ids) > 0 else 0,
                    }

                    # Safely add optional fields
                    if mo.product_uom_id:
                        mo_data['product_uom_id'] = mo.product_uom_id.id
                        mo_data['product_uom'] = mo.product_uom_id.name
                    else:
                        mo_data['product_uom_id'] = None
                        mo_data['product_uom'] = None

                    if mo.company_id:
                        mo_data['company_id'] = mo.company_id.id
                        mo_data['company_name'] = mo.company_id.name
                    else:
                        mo_data['company_id'] = None
                        mo_data['company_name'] = None

                    if mo.bom_id:
                        mo_data['bom_id'] = mo.bom_id.id
                        mo_data['bom_name'] = mo.bom_id.display_name
                    else:
                        mo_data['bom_id'] = None
                        mo_data['bom_name'] = None

                    if mo.user_id:
                        mo_data['user_id'] = mo.user_id.id
                        mo_data['user_name'] = mo.user_id.name
                    else:
                        mo_data['user_id'] = None
                        mo_data['user_name'] = None

                    # Dates
                    mo_data['date_planned_start'] = str(mo.date_start) if getattr(mo, 'date_start', None) else None
                    mo_data['date_planned_finished'] = str(mo.date_planned_finished) if getattr(mo,
                                                                                                'date_planned_finished',
                                                                                                None) else None
                    mo_data['date_deadline'] = str(mo.date_deadline) if getattr(mo, 'date_deadline', None) else None
                    mo_data['date_finished'] = str(mo.date_finished) if getattr(mo, 'date_finished', None) else None

                    # Other optional fields
                    mo_data['origin'] = mo.origin if getattr(mo, 'origin', None) else None
                    mo_data['priority'] = mo.priority if hasattr(mo, 'priority') else None
                    mo_data['raw_materials_count'] = len(mo.move_raw_ids) if getattr(mo, 'move_raw_ids', None) else 0

                    data.append(mo_data)

                except Exception as mo_error:
                    # Skip this MO if there's an error, but continue with others
                    continue

            res = ApiResult(200, payload=data)
            return Response(json.dumps(res.to_dict()), status=200, content_type='application/json')

        except Exception as ex:
            import traceback
            traceback.print_exc()
            res = ApiResult(500, error=f"Manufacturing orders listesi alınırken hata: {str(ex)}")
            return Response(json.dumps(res.to_dict()), status=500, content_type='application/json')

    @http.route('/api/manufacturing-orders/<int:mo_id>', type='http', auth='none', methods=['GET'], csrf=False)
    @jwt_required
    def get_manufacturing_order_by_id(self, mo_id, **kwargs):
        try:
            # Get superuser environment
            env = request.env(user=1)

            # Find specific MO
            mo = env['mrp.production'].browse(mo_id)
            if not mo.exists():
                res = ApiResult(404, error=f"Manufacturing Order bulunamadı (ID: {mo_id})")
                return Response(json.dumps(res.to_dict()), status=404, content_type='application/json')

            # Work orders basic bilgileri - only safe fields
            workorders = []
            for wo in mo.workorder_ids.sorted(key=lambda w: w.id):
                wo_data = {
                    'wo_id': wo.id,
                    'wo_name': wo.name,
                    'wo_state': wo.state,
                }

                # Only add fields that definitely exist
                if hasattr(wo, 'operation_id') and wo.operation_id:
                    wo_data['operation_id'] = wo.operation_id.id
                    wo_data['operation_name'] = wo.operation_id.name
                else:
                    wo_data['operation_id'] = None
                    wo_data['operation_name'] = None

                if hasattr(wo, 'workcenter_id') and wo.workcenter_id:
                    wo_data['workcenter_id'] = wo.workcenter_id.id
                    wo_data['workcenter_name'] = wo.workcenter_id.name
                else:
                    wo_data['workcenter_id'] = None
                    wo_data['workcenter_name'] = None

                # Add duration information
                wo_data['duration_expected'] = getattr(wo, 'duration_expected', 0)
                wo_data['duration_actual'] = getattr(wo, 'duration', 0)
                wo_data['duration_difference'] = wo_data['duration_actual'] - wo_data['duration_expected'] if wo_data[
                                                                                                                  'duration_expected'] > 0 else 0

                # Add quantity information
                wo_data['qty_production'] = getattr(wo, 'qty_production', 0)
                wo_data['qty_produced'] = getattr(wo, 'qty_produced', 0)
                wo_data['qty_remaining'] = getattr(wo, 'qty_remaining', 0)

                workorders.append(wo_data)

            # Work order durumları sayısı
            ready_count = sum(1 for w in mo.workorder_ids if w.state == 'ready')
            progress_count = sum(1 for w in mo.workorder_ids if w.state == 'progress')
            done_count = sum(1 for w in mo.workorder_ids if w.state == 'done')
            waiting_count = sum(1 for w in mo.workorder_ids if w.state == 'pending')
            cancel_count = sum(1 for w in mo.workorder_ids if w.state == 'cancel')

            # Build MO data safely
            mo_data = {
                'mo_id': mo.id,
                'mo_name': mo.name,
                'mo_state': mo.state,
                'product_id': mo.product_id.id if mo.product_id else None,
                'product_code': mo.product_id.default_code if mo.product_id else None,
                'product_name': mo.product_id.display_name if mo.product_id else None,
                'product_qty': mo.product_qty,
                'qty_produced': getattr(mo, 'qty_produced', 0),
                'create_date': str(mo.create_date),
                'write_date': str(mo.write_date),

                # Work Order Counts
                'total_workorders': len(mo.workorder_ids),
                'waiting_workorders': waiting_count,
                'ready_workorders': ready_count,
                'in_progress_workorders': progress_count,
                'done_workorders': done_count,
                'cancelled_workorders': cancel_count,

                # Detailed Work Orders
                'workorders': workorders,

                # Progress Calculation
                'progress_percentage': round((done_count / len(mo.workorder_ids) * 100), 2) if len(
                    mo.workorder_ids) > 0 else 0,
            }

            # Safely add optional fields
            if mo.product_uom_id:
                mo_data['product_uom_id'] = mo.product_uom_id.id
                mo_data['product_uom'] = mo.product_uom_id.name
            else:
                mo_data['product_uom_id'] = None
                mo_data['product_uom'] = None

            if mo.company_id:
                mo_data['company_id'] = mo.company_id.id
                mo_data['company_name'] = mo.company_id.name
            else:
                mo_data['company_id'] = None
                mo_data['company_name'] = None

            if mo.bom_id:
                mo_data['bom_id'] = mo.bom_id.id
                mo_data['bom_name'] = mo.bom_id.display_name
            else:
                mo_data['bom_id'] = None
                mo_data['bom_name'] = None

            if mo.user_id:
                mo_data['user_id'] = mo.user_id.id
                mo_data['user_name'] = mo.user_id.name
            else:
                mo_data['user_id'] = None
                mo_data['user_name'] = None

            # Dates
            mo_data['date_planned_start'] = str(mo.date_start) if getattr(mo, 'date_start', None) else None
            mo_data['date_planned_finished'] = str(mo.date_planned_finished) if getattr(mo, 'date_planned_finished',
                                                                                        None) else None
            mo_data['date_deadline'] = str(mo.date_deadline) if getattr(mo, 'date_deadline', None) else None
            mo_data['date_finished'] = str(mo.date_finished) if getattr(mo, 'date_finished', None) else None

            # Other optional fields
            mo_data['origin'] = mo.origin if getattr(mo, 'origin', None) else None
            mo_data['priority'] = mo.priority if hasattr(mo, 'priority') else None
            mo_data['raw_materials_count'] = len(mo.move_raw_ids) if getattr(mo, 'move_raw_ids', None) else 0

            res = ApiResult(200, payload=mo_data)
            return Response(json.dumps(res.to_dict()), status=200, content_type='application/json')

        except Exception as ex:
            import traceback
            traceback.print_exc()
            res = ApiResult(500, error=f"Manufacturing Order alınırken hata: {str(ex)}")
            return Response(json.dumps(res.to_dict()), status=500, content_type='application/json')

    @http.route('/api/mo/create', type='http', auth='none', methods=['POST'], csrf=False)
    @jwt_required
    def create_mo(self, **kwargs):
        # Fix: Proper parameter extraction for HTTP JSON requests
        try:
            # Extract params
            if request.httprequest.content_type == 'application/json':
                body = json.loads(request.httprequest.get_data(as_text=True))
                if 'params' in body:
                    params = body['params']
                else:
                    params = body
            else:
                params = kwargs
        except Exception as e:
            res = ApiResult(400, error="Invalid JSON request")
            return Response(json.dumps(res.to_dict()), status=400, content_type='application/json')

        # 1) Validasyon
        product_code = params.get('product_code')
        qty_raw = params.get('product_quantity')

        if not product_code or not str(product_code).strip():
            res = ApiResult(400, error="product_code boş gönderilemez.")
            return Response(json.dumps(res.to_dict()), status=400, content_type='application/json')

        try:
            qty = float(qty_raw)
        except (TypeError, ValueError):
            res = ApiResult(400, error="product_quantity sayısal olmalıdır.")
            return Response(json.dumps(res.to_dict()), status=400, content_type='application/json')

        if qty <= 0:
            res = ApiResult(400, error="product_quantity > 0 olmalıdır.")
            return Response(json.dumps(res.to_dict()), status=400, content_type='application/json')

        code = str(product_code).strip()

        try:
            # Get superuser environment to avoid singleton errors
            Env = request.env(user=1)  # user=1 is superuser/admin
            Product = Env['product.product']
            Bom = Env['mrp.bom']
            Mrp = Env['mrp.production']

            # 2) Ürün arama
            products = Product.search([('default_code', '=', code)])
            if not products:
                res = ApiResult(404, error=f"Ürün bulunamadı (default_code={code}).")
                return Response(json.dumps(res.to_dict()), status=404, content_type='application/json')
            if len(products) > 1:
                res = ApiResult(400, error="Aynı default_code ile birden fazla ürün var.")
                return Response(json.dumps(res.to_dict()), status=400, content_type='application/json')
            product = products[0]

            # Fix: Use proper company access with superuser context
            try:
                # First try to get company from superuser environment
                company_id = Env.company.id
                if not company_id:
                    # Get the first company as fallback
                    company_id = Env['res.company'].search([], limit=1).id
            except:
                # Last resort - get the first company
                company_id = Env['res.company'].search([], limit=1).id

            if not company_id:
                res = ApiResult(500, error="Şirket bulunamadı. Sistem yapılandırması kontrol edilmelidir.")
                return Response(json.dumps(res.to_dict()), status=500, content_type='application/json')

            # 3) BOM seçimi - Fixed logic
            bom = False
            bom_id_param = params.get('bom_id')
            bom_code_param = params.get('bom_code')

            if bom_id_param is not None:
                try:
                    b_id = int(bom_id_param)
                except (TypeError, ValueError):
                    res = ApiResult(400, error="bom_id sayısal olmalıdır.")
                    return Response(json.dumps(res.to_dict()), status=400, content_type='application/json')
                b = Bom.browse(b_id)
                if not b.exists():
                    res = ApiResult(404, error="bom_id bulunamadı.")
                    return Response(json.dumps(res.to_dict()), status=404, content_type='application/json')
                bom = b
            elif bom_code_param:
                b = Bom.search([
                    ('code', '=', str(bom_code_param).strip()),
                    ('company_id', '=', company_id),
                    ('product_tmpl_id', '=', product.product_tmpl_id.id),
                ], limit=1)
                if not b:
                    res = ApiResult(404, error="Belirtilen bom_code için BOM bulunamadı.")
                    return Response(json.dumps(res.to_dict()), status=404, content_type='application/json')
                bom = b
            else:
                # Auto-find BOM - Fixed with proper error handling
                bom = False

                # Manual search - most reliable approach
                bom = Bom.search([
                    ('company_id', '=', company_id),
                    ('product_tmpl_id', '=', product.product_tmpl_id.id),
                    ('active', '=', True),
                ], order='sequence, id', limit=1)

                if not bom:
                    # Try to find any BOM for this product template (without company restriction)
                    bom = Bom.search([
                        ('product_tmpl_id', '=', product.product_tmpl_id.id),
                        ('active', '=', True),
                    ], order='sequence, id', limit=1)

            # Safe display name access
            bom_name = "None"
            if bom and hasattr(bom, 'display_name'):
                bom_name = bom.display_name
            elif bom and hasattr(bom, 'name'):
                bom_name = bom.name
            elif bom:
                bom_name = f"BOM-{bom.id}"

            # 4) UoM - Fixed validation
            uom_id = params.get('product_uom_id')
            if uom_id is not None:
                try:
                    uom_id = int(uom_id)
                    # Validate UoM exists
                    uom = Env['uom.uom'].browse(uom_id)
                    if not uom.exists():
                        res = ApiResult(404, error="product_uom_id geçersiz.")
                        return Response(json.dumps(res.to_dict()), status=404, content_type='application/json')
                except (TypeError, ValueError):
                    res = ApiResult(400, error="product_uom_id sayısal olmalıdır.")
                    return Response(json.dumps(res.to_dict()), status=400, content_type='application/json')
            else:
                uom_id = product.uom_id.id

            # 5) MO oluştur - Fixed values dictionary with proper company
            vals = {
                'product_id': product.id,
                'product_qty': qty,
                'product_uom_id': uom_id,
            }

            # Only add company_id if it's valid
            if company_id and isinstance(company_id, int):
                vals['company_id'] = company_id

            # Only add BOM if found and is a valid record
            if bom and hasattr(bom, 'id') and bom.id:
                vals['bom_id'] = bom.id

            # Add optional fields
            origin = params.get('origin')
            if origin:
                vals['origin'] = str(origin)

            date_planned_start = params.get('date_planned_start')
            if date_planned_start:
                vals['date_start'] = date_planned_start  # Fixed field name

            # Create MO with superuser context
            mo = Mrp.create(vals)

            # Auto-confirm if requested
            if params.get('confirm'):
                try:
                    mo.action_confirm()
                except Exception as confirm_error:
                    _logger = logging.getLogger(f"Confirmation error: {confirm_error}")
                    #print(f"Confirmation error: {confirm_error}")
                    # Don't fail the entire operation, just log the error

            res = ApiResult(201, payload={'id': mo.id, 'name': mo.name, 'state': mo.state})
            return Response(json.dumps(res.to_dict()), status=201, content_type='application/json')

        except Exception as ex:
            res = ApiResult(500, error=f"MO oluşturulurken hata: {str(ex)}")
            return Response(json.dumps(res.to_dict()), status=500, content_type='application/json')