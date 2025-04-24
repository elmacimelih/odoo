# -*- coding: utf-8 -*-

# from odoo import http
#
# class StudentAPI(http.Controller):
#
#     @http.route('/update_fees', auth='none', type='http')
#     def update_fees(self, **kw):
#         return "<h1>Hello world!</h1>"


from odoo import http
from odoo.http import request

class StudentAPI(http.Controller):

    @http.route('/api/student/update_fees', type='json', auth='none', methods=['POST'], csrf=False)
    def update_fees(self, **kwargs):
        # user = request.env.user
        # if not user.has_group('module_name.group_school_manager'):
        #     return {'error': 'Bu işlem için yetkiniz yoktur'}

        student_id = kwargs.get('student_id')
        amount = kwargs.get('amount')
        print(student_id, amount)
        if not student_id or not amount:
            return {'error': 'student_id ve amount zorunludur.'}

        student = request.env['wb.student'].sudo().browse(student_id)

        if not student.exists():
            return {'error': 'Öğrenci bulunamadı.'}

        student.student_fees -= amount

        return {
            'success': True,
            'student_id': student.id,
            'new_fees': student.student_fees
        }
