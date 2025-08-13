from odoo import api, fields, models


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    meter_id = fields.Char(string='Meter ID', related='partner_id.meter_id', readonly=True)
    reference_no = fields.Char(string='Reference Number', related='partner_id.reference_no',
                               readonly=True)
    is_bill = fields.Boolean('Is Bill')
    billing_month = fields.Date(string='Billing Month')
    reading_date = fields.Date(string='Reading Date')
    issue_date = fields.Date(string='Issue Date')
    mf_value = fields.Float(string='MF')
    previous_reading_unit = fields.Float(string='Previous Reading (Auto)', compute='_compute_previous_reading_unit',
                                         store=True)

    electric_bill_image = fields.Binary(string='Electric Bill Image')
    complaint_mobile_number = fields.Char(string='Mobile(Complaint)', default='03014630923')
    complaint_ptcl_number = fields.Char(string='PTCL No', default='04235759157(EXT 114)')

    late_payment_surcharge = fields.Float(string='Late Payment Surcharge')

    bill_notes = fields.Text(string='Bill Notes')
    signatory_name_1 = fields.Char(string='Signatory Name 1')
    signatory_name_2 = fields.Char(string='Signatory Name 2')
    signatory_name_3 = fields.Char(string='Signatory Name 3')

    @api.depends('partner_id', 'is_bill', 'date')
    def _compute_previous_reading_unit(self):
        for move in self:
            if move.is_bill and move.partner_id:
                # Search for the most recent posted bill for the same partner
                last_bill = self.env['account.move'].search([
                    ('partner_id', '=', move.partner_id.id),
                    ('is_bill', '=', True),
                    ('state', '=', 'posted'),
                    ('billing_month', '<', move.billing_month or fields.Date.today()),
                    ('id', '!=', move.id),
                ], order='billing_month desc', limit=1)

                print(f'Last billing month: {last_bill}')

                if last_bill and last_bill.invoice_line_ids:
                    # Get the next_reading_unit from the last bill's line (assuming one line per bill)
                    move.previous_reading_unit = last_bill.invoice_line_ids[0].next_reading_unit
                else:
                    move.previous_reading_unit = 0.0
            else:
                move.previous_reading_unit = 0.0
                move.partner_id.partner_previous_reading = 0.0


class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    previous_reading_unit = fields.Float(string='Previous Reading', digits=(10, 2))
    next_reading_unit = fields.Float(string='Next Reading', digits=(10, 2))
    # consumed_unit = fields.Float(string='Consumed Unit', digits=(10, 2), compute='_compute_consumed_unit', store=True)

    quantity = fields.Float(
        string='Quantity',
        compute='_compute_quantity',
        store=True,
        readonly=False,
        precompute=True,
        digits='Product Unit of Measure',
        help="Auto-calculated based on reading if is_bill is True. Otherwise defaults to 1.",
    )

    @api.depends('previous_reading_unit', 'next_reading_unit', 'move_id.is_bill', 'move_id.move_type', 'display_type')
    def _compute_quantity(self):
        for rec in self:
            if rec.display_type != 'product':
                rec.quantity = False
            elif (
                    rec.move_id
                    and rec.move_id.is_bill
                    and rec.move_id.move_type == 'out_invoice'
            ):
                rec.quantity = (rec.next_reading_unit or 0.0) - (rec.previous_reading_unit or 0.0)
            else:
                rec.quantity = rec.quantity or 1

    @api.onchange('next_reading_unit', 'move_id')
    def _onchange_next_reading_unit(self):
        for rec in self:
            if not rec.next_reading_unit or not rec.move_id:
                continue
            partner = rec.move_id.partner_id
            if not partner:
                continue
            partner.partner_previous_reading = rec.next_reading_unit

            partner.write({'partner_previous_reading': rec.next_reading_unit})
