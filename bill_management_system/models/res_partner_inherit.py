from odoo import _, api, fields, models


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    meter_id = fields.Char(string='Meter ID', required=True)
    reference_no = fields.Char(string='Reference Number', required=True)
    partner_previous_reading = fields.Float(string='Previous Reading Unit', readonly=True)
    cnic = fields.Char(string='CNIC', required=True)
