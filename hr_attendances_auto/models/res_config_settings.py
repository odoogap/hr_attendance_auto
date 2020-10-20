from odoo import models, fields, api, exceptions, _


class ReConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    company_timezone = fields.Char(String="Region:", config_parameter='hr_attendance_auto.company_timezone')
    in_out_times = fields.Char(String="Check times:", config_parameter='hr_attendance_auto.in_out_times')
