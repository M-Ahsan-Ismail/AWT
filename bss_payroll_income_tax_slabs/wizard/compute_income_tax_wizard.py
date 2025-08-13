from odoo import models, fields, api
from odoo.exceptions import UserError


class ComputeIncomeTaxWizard(models.TransientModel):
    _name = 'income.tax.wizard'
    _description = 'Compute Income Tax Wizard'

    slab_id = fields.Many2one('tax.slab', required=True, readonly=False)
    contract_ids = fields.Many2many('hr.contract', string='Contracts',
                                    default=lambda self: self.env.context.get('active_ids', []))

    def action_confirm(self):
        for wizard in self:
            if not wizard.slab_id:
                raise UserError("Please select a tax slab.")
            if not wizard.contract_ids:
                raise UserError("No contracts selected to compute income tax.")

            for contract in wizard.contract_ids:
                tax_amount = self.calculate_income_tax(contract.wage, wizard.slab_id)
                contract.write({'income_tax_amount': tax_amount})

    def calculate_income_tax(self, wage, tax_slab):
        gross_salary = wage * 12
        tax_amount = 0
        for line in tax_slab.tax_slab_line_ids:
            if gross_salary >= line.year_start_limit and gross_salary < line.year_end_limit:
                tax_amount += ((gross_salary - line.year_start_limit) * line.tax_rate) + line.fixed_amount
        return round(tax_amount / 12)