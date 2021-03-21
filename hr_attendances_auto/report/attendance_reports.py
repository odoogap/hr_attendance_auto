from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import datetime
import calendar
from psycopg2.extensions import AsIs


class AttendanceReportMonthly(models.AbstractModel):
    _name = 'report.monthly.attendance'

    def _get_ending_balances(self, account_id, date_from, date_to, partner_id=False):
        query = """
        SELECT 
            row_number() OVER () as rnum,
            t.partner_id,
            t.name,
            t.debits,
            t.credits,
            t.balance
          FROM (
            SELECT aml.partner_id, p.name, sum(aml.debit) debits, sum(aml.credit) credits, sum(aml.credit) - sum(aml.debit) balance
            FROM account_move_line aml INNER JOIN res_partner p ON (p.id = aml.partner_id)
            WHERE aml.account_id=%(account_id)s and aml.date <=%(date_to)s %(sql_where)s
            GROUP BY 1,2
        ) t;
        """
        vals = {
            'account_id': account_id,
            'date_from': date_from,
            'date_to': date_to,
            'sql_where': partner_id and AsIs(" and aml.partner_id=%s" % partner_id) or AsIs(" and true"),
        }
        self.env.cr.execute(query, vals)
        return self.env.cr.dictfetchall()

    def _get_html(self):
        result = {}
        rcontext = {}
        context = dict(self.env.context)
        rcontext['lines'] = self.with_context(context).get_lines()
        result['html'] = self.env.ref('stock.report_stock_inventory').render(rcontext)
        return result

    @api.model
    def get_html(self, given_context=None):
        res = self.search([('create_uid', '=', self.env.uid)], limit=1)
        if not res:
            return self.create({}).with_context(given_context)._get_html()
        return res.with_context(given_context)._get_html()

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        employee_id = data['form']['employee_id']
        print ("------   RENDER ------")
        holidays = self.env['hr.employee'].browse(self.ids)
        return {
            'doc_ids': self.ids,
            'doc_model': self.env['ir.actions.report']._get_report_from_name('hr_attendances_auto.action_report_attendance_sheet').model,
            'docs': holidays,
            'date_from': data['form']['date_from'],
            'date_to': data['form']['date_to'],
            'employee_id': data['form']['employee_id'],
        }


class AttendanceReportWiz(models.TransientModel):
    _name = "attendance.report.wiz"
    _description = "Three Way Report Wizard"

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    date_from = fields.Date("Start Date", required=True, default=datetime.now().strftime('%Y-%m-01'))
    date_to = fields.Date(
        "End Date",
        required=True,
        default=datetime.now().replace(day=calendar.monthrange(datetime.now().year, datetime.now().month)[1]).date())
    employee_id = fields.Many2one('hr.employee', string="Employee", default=_default_employee, required=True, ondelete='cascade', index=True)

    @api.multi
    def button_report(self):
        self.ensure_one()
        wiz = self.read(['date_from', 'date_to', 'employee_id'])[0]
        data = {
            'form': wiz
        }
        return self.env.ref('hr_attendances_auto.action_report_attendance_sheet').report_action(self, data=data, config=False)
