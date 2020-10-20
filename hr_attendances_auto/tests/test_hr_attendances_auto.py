# -*- coding: utf-8 -*-
from odoo.tests import common, Form


class TestHrAttendanceAuto(common.TransactionCase):

    # test for date(2020-10-1)
    # You need remove default attendances
    def test_value(self):
        self.env['ir.config_parameter'].set_param('hr_attendances_auto.company_timezone', 'Europe/Lisbon')
        user = self.env['res.users'].search_count([('name', '=', 'Simao Duarte')])
        if user == 0:
            attendance_user = self.env['res.users'].create({
                'name': 'Simao Duarte',
                'login': 'simao',
                'email': 'simao@yourcompany.com',
                'company_id': self.env.ref('base.main_company').id,
                'groups_id': [(6, 0, [
                    self.ref('base.group_user'),
                    self.ref('hr_attendance.group_hr_attendance')
                ])]
            })
            self.env['hr.employee'].search([('name', '=', 'Anita Oliver')]).write({
                'user_id': attendance_user.id
            })
        self.env['hr.employee'].browse().auto_attendance()
        count = self.env['hr.attendance'].search_count([('employee_id', '=', 'Simao Duarte')])
        self.assertEquals(count, 42)
