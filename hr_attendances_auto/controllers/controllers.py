# -*- coding: utf-8 -*-
from odoo import http

# class HrAttendancesAuto(http.Controller):
#     @http.route('/hr_attendances_auto/hr_attendances_auto/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_attendances_auto/hr_attendances_auto/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_attendances_auto.listing', {
#             'root': '/hr_attendances_auto/hr_attendances_auto',
#             'objects': http.request.env['hr_attendances_auto.hr_attendances_auto'].search([]),
#         })

#     @http.route('/hr_attendances_auto/hr_attendances_auto/objects/<model("hr_attendances_auto.hr_attendances_auto"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_attendances_auto.object', {
#             'object': obj
#         })