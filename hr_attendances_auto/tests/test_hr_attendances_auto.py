# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase, tagged
from odoo.tests import common, Form
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import date
from datetime import timedelta
from dateutil.relativedelta import relativedelta


def next_day():
    day = date.today().replace(day=1)
    month = day.month
    while day.month == month:
        yield day
        day = day + timedelta(days=1)


class TestHrAttendanceAuto(common.TransactionCase):

    def holiday_day(self):
        x = 0
        today = date.today().replace(day=1)
        next_month = today + relativedelta(months=1)
        this_month_str = today.strftime(DEFAULT_SERVER_DATE_FORMAT)
        next_month_str = next_month.strftime(DEFAULT_SERVER_DATE_FORMAT)
        holidays_list = [s['date_holidays'] for s in self.env['public.holiday'].search_read([
            ('date_holidays', '>=', this_month_str),
            ('date_holidays', '<', next_month_str),
        ], ['date_holidays'])]
        for day in [i for i in next_day()]:
            if day.weekday() in (5, 6) or day in holidays_list:
                continue
            else:
                x += 1
        x = x * 2
        return x

    def test_value(self):
        self.env['ir.config_parameter'].set_param('hr_attendances_auto.company_timezone', 'Europe/Lisbon')
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
        number = self.holiday_day()
        self.assertEquals(count, number)
