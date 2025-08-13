from odoo import models, fields, api


class HRContractInherit(models.AbstractModel):
    _inherit = 'hr.contract'

    income_tax_amount = fields.Float(
        string='Monthly Income Tax',
        help="Computed monthly income tax based on the applied tax slab.",
        default=0.0,
    )
