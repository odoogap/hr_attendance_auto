# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
import datetime
from datetime import datetime
from pytz import timezone
import pytz
from datetime import date
from datetime import timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil.relativedelta import relativedelta
import json
import traceback


class PublicHoliday(models.Model):
    _name = 'public.holiday'

    name = fields.Char("Holiday Name")
    date_holidays = fields.Date(string="Holidays")
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    _sql_constraints = [
        ('day_year_uniq', 'unique(date_holidays, company_id)',
         'This day is repeated for the same year!'),
    ]


# This function give all days of current month
def next_day(day):
    month = day.month
    while day.month == month:
        yield day
        day = day + timedelta(days=1)


class Attendance(models.Model):
    _inherit = 'hr.attendance'

    user_id = fields.Many2one('res.users', 'User', related='employee_id.user_id', store=True, readonly=False)

    def cron_send_email_reports(self):
        qweb = self.env['ir.qweb'].sudo()
        for employee in self.env['hr.employee'].search([('user_id', '!=', False)]):
            d1 = (datetime.today().replace(day=1) - relativedelta(months=1)).date()
            domain = lambda x: [
                ('employee_id', '=', employee.id),
                ('check_in', '>=', x),
                ('check_in', '<=', x),
            ]
            lines = []
            for day in [i for i in next_day(d1)]:
                note = ", ".join([
                    "%(check_in)s to %(check_out)s " % {
                        'check_in': d.check_in and d.check_in.strftime("%H:%M") or '',
                        'check_out': d.check_out and d.check_out.strftime("%H:%M") or ''
                    } for d in self.env['hr.attendance'].search(domain(day), order='check_in')])
                style = day.weekday() in (5, 6) and 'background-color: yellow' or ''
                lines.append(dict(day=day, note=note, style=style))
            content = qweb.render("hr_attendances_auto.email_template_check_attendances", {
                'title': _('Please check your last months attendance:'),
                'lines': lines
            })
            mail = self.env['mail.mail'].create({
                'subject': _('Monthly Attendance Report %s') % d1.strftime('%B-%Y'),
                'email_to': employee.user_id.partner_id.email,
                'body_html': content,
            })
            mail.send()


class Employee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def auto_attendance(self, today=date.today().replace(day=1), employee=False):
        # echo "from datetime import date; today=date(2020,10,11);env['hr.employee'].auto_attendance(today=today, employee='Diogo')" | odoogap-shell -d v12_odoogap
        if employee:
            employees = self.env['hr.employee'].search([('user_id', 'ilike', employee)])
        else:
            employees = self.env['hr.employee'].search([('user_id', '!=', False)])
        today = today.replace(day=1)
        next_month = today + relativedelta(months=1)
        try:
            company_timezone = self.env['ir.config_parameter'].get_param('hr_attendance_auto.company_timezone')

            this_month_str = today.strftime(DEFAULT_SERVER_DATE_FORMAT)
            next_month_str = next_month.strftime(DEFAULT_SERVER_DATE_FORMAT)
            holidays_list = [s['date_holidays'] for s in self.env['public.holiday'].search_read([
                ('date_holidays', '>=', this_month_str),
                ('date_holidays', '<', next_month_str),
            ], ['date_holidays'])]
            for day in [i for i in next_day(today)]:
                if day.weekday() in (5, 6) or day in holidays_list:
                    continue
                else:
                    my_datetime = datetime.combine(day, datetime.min.time())
                    for rec in employees:
                        hour = json.loads(self.env['ir.config_parameter'].get_param('hr_attendance_auto.in_out_times'))
                        try:
                            for timer in hour[0]:
                                final_hour = hour[0][timer]
                                check_in_datetime = my_datetime.replace(hour=final_hour[0], minute=0, second=0, microsecond=0)
                                check_out_datetime = my_datetime.replace(hour=final_hour[1], minute=0, second=0, microsecond=0)
                                check_in_str = fields.Datetime.from_string(check_in_datetime)
                                check_out_str = fields.Datetime.from_string(check_out_datetime)
                                check_in_final = timezone(company_timezone).localize(check_in_str).astimezone(pytz.UTC)
                                check_out_final = timezone(company_timezone).localize(check_out_str).astimezone(pytz.UTC)
                                self.env['hr.attendance'].create([
                                    {
                                        'employee_id': rec.id,
                                        'check_in': check_in_final,
                                        'check_out': check_out_final,
                                    },
                                ])

                            self.env.cr.commit()
                        except exceptions.ValidationError as e:
                            self.env.cr.rollback()
                            continue

        except Exception:
            self.env.cr.rollback()
            traceback.print_exc()
