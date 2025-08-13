from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PayrollIncomeTaxSlab(models.Model):
    _name = 'tax.slab'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Income Tax Slab'
    _order = 'name'

    name = fields.Char(
        string='Slab Name',
        required=True,
        index=True,
        help="Name of the income tax slab (e.g., FY 2024-25)"
    )
    tax_slab_line_ids = fields.One2many(
        'tax.slab.line',
        'tax_slab_id',
        string='Slab Lines',
        help="Define multiple slab ranges and their corresponding tax rates."
    )
    slab_lines_summary = fields.Html(
        string='Slab Lines Summary',
        compute='_compute_slab_lines_summary',
        help="Formatted summary of tax slab lines for display."
    )

    @api.depends('tax_slab_line_ids')
    def _compute_slab_lines_summary(self):
        for record in self:
            lines = record.tax_slab_line_ids.sorted(key='year_start_limit')
            summary = '<ul style="list-style: none; padding: 0; margin: 8px 0;">'
            for line in lines:
                summary += f'<li style="padding: 4px 0; border-left: 3px solid #714B67; padding-left: 8px; margin-bottom: 4px;">{line.year_start_limit:.2f} - {line.year_end_limit:.2f}: <strong>{line.tax_rate:.2f}%</strong> (Fixed: {line.fixed_amount:.2f})</li>'
            summary += '</ul>'
            record.slab_lines_summary = summary if lines else '<em style="color: #888; font-style: italic;">No tax slab lines defined.</em>'


class PayrollIncomeTaxSlabLine(models.Model):
    _name = 'tax.slab.line'
    _description = 'Income Tax Slab Line'
    _order = 'year_start_limit'

    tax_slab_id = fields.Many2one(
        'tax.slab',
        string='Tax Slab',
        ondelete='cascade'
    )

    year_start_limit = fields.Float(
        string='Start Limit (Annual)',
        help="Start of income range for this tax slab line."
    )
    year_end_limit = fields.Float(
        string='End Limit (Annual)',
        help="End of income range for this tax slab line."
    )
    tax_rate = fields.Float(
        string='Tax Rate (%)',
        help="Percentage tax rate applicable for this income range."
    )
    fixed_amount = fields.Float(
        string='Fixed Amount',
        required=True,
        help="Fixed tax amount applicable before applying the percentage."
    )

    @api.constrains('tax_rate')
    def _check_tax_rate(self):
        for rec in self:
            if not 0 <= rec.tax_rate <= 100:
                raise ValidationError("Tax Rate must be between 0% and 100%.")

    @api.constrains('year_start_limit', 'year_end_limit')
    def _check_limits(self):
        for rec in self:
            if rec.year_start_limit >= rec.year_end_limit:
                raise ValidationError("Start limit must be less than end limit.")
