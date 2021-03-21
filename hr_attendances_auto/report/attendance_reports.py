from odoo import _, api, fields, models
from dateutil.relativedelta import relativedelta
from datetime import timedelta


# This function give all days of current month
def next_day(day):
    month = day.month
    while day.month == month:
        yield day
        day = day + timedelta(days=1)


class ReportAttendanceSheet(models.AbstractModel):
    _name = 'report.hr_attendances_auto.report_attendance_sheet'
    _description = 'Attendance report'

    @api.model
    def _get_report_values(self, docids, data=None):
        data = data if data is not None else {}
        d1 = fields.Date.from_string(data['form']['d1'])
        employee_id = data['form']['employee_id'][0]
        domain = lambda x: [
            ('employee_id', '=', employee_id),
            ('check_in', '>=', x),
            ('check_in', '<=', x),
        ]
        lines = []
        for day in next_day(d1):

            line_ids = self.env['hr.attendance'].search(domain(day), order='check_in')
            lines.append({
                'day': fields.Date.to_string(day),
                'line_ids': [{
                    'in': l.check_in.strftime("%H:%M:%S"),
                    'out': l.check_out.strftime("%H:%M:%S"),
                } for l in line_ids]
            })

        return {
            'doc_ids': data.get('ids', data.get('active_ids')),
            'doc_model': 'hr.attendance',
            'lines': lines,
            'data': dict(
                data,
            ),
        }


class AttendanceReportWiz(models.TransientModel):
    _name = "attendance.report.wiz"
    _description = "Three Way Report Wizard"

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    @api.model
    def _compute_month(self):
        """ This routine will generate the selection"""
        self.env.cr.execute("""
        SELECT DISTINCT to_char(check_in, 'YYYY-MM') month_period
        FROM hr_attendance
        ORDER BY 1 desc;
        """)
        sel = self.env.cr.dictfetchall()
        return [(s['month_period'], s['month_period']) for s in sel]

    month_period = fields.Selection('_compute_month', string='Month Period', required=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", default=_default_employee, required=True, ondelete='cascade', index=True)

    @api.multi
    def print_report(self):
        self.ensure_one()
        d1 = fields.Date.from_string("%s-01" % self.month_period)
        d2 = d1 + relativedelta(months=+1, days=-1)
        [form] = self.read()
        form.update({
            'd1': d1,
            'd2': d2,
        })
        doc_ids = self.env['hr.attendance'].search([], limit=50)
        datas = {
            'ids': doc_ids.ids,
            'model': 'hr.attendance',
            'form': form,

        }
        return self.env.ref('hr_attendances_auto.action_report_attendance_sheet').report_action([], data=datas)
