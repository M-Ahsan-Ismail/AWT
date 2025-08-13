import base64
from odoo import http, fields, _
from odoo.exceptions import ValidationError
from odoo.http import request


class CreateBillRecord(http.Controller):
    @http.route('/create/electric/bill', type='http', auth='user', website=True, methods=['GET', 'POST'], csrf=True)
    def CreateElectricBill(self, **post):
        res_partner_list = []
        partner_recs = request.env['res.partner'].sudo().search([])
        for partner in partner_recs:
            res_partner_list.append({
                'id': partner.id, 'name': partner.name, 'meter_id': partner.meter_id,
                'reference_no': partner.reference_no, 'previous_reading_unit': partner.partner_previous_reading,
            })

        if request.httprequest.method == 'POST':
            partner_id = int(post.get('partner_id'))
            meter_id = post.get('meter_id')
            reference_no = post.get('reference_no')
            next_reading_value = float(post.get('next_reading_value'))
            billing_month = fields.Date.from_string(post.get('billing_month')) if post.get('billing_month') else False
            reading_date = fields.Date.from_string(post.get('reading_date')) if post.get('reading_date') else False
            issue_date = fields.Date.from_string(post.get('issue_date')) if post.get('issue_date') else False
            due_date = fields.Date.from_string(post.get('due_date')) if post.get('due_date') else False

            # Image Field
            image_file = request.httprequest.files.get('image_1920')
            image_base64 = False
            image_base64 = base64.b64encode(image_file.read()) if image_file else False

            # Line Data
            invoice_lines = []

            product = request.env['product.product'].search([('name', '=', 'Units')], limit=1)
            if product:
                invoice_lines.append((0, 0, {
                    'product_id': product.id,
                    'next_reading_unit': next_reading_value,
                }))

            account_700001 = request.env['account.account'].search([('code', '=', '700001')], limit=1)
            if account_700001:
                invoice_lines.append((0, 0, {
                    'account_id': account_700001.id,
                }))

            # Line 3: Account 251005
            account_251005 = request.env['account.account'].search([('code', '=', '251005')], limit=1)
            if account_251005:
                invoice_lines.append((0, 0, {
                    'account_id': account_251005.id,
                }))

            # Line 4  Account 251006
            account_251006 = request.env['account.account'].search([('code', '=', '251006')], limit=1)
            if account_251006:
                invoice_lines.append((0, 0, {
                    'account_id': account_251006.id,
                }))

            # Line 5  Account 251007
            account_251007 = request.env['account.account'].search([('code', '=', '251007')], limit=1)
            if account_251007:
                invoice_lines.append((0, 0, {
                    'account_id': account_251007.id,
                }))

            # Step 2: Create the invoice (account.move)
            invoice_vals = {
                'move_type': 'out_invoice',
                'is_bill': True,
                'partner_id': partner_id,
                'meter_id': meter_id,
                'reference_no': reference_no,
                'billing_month': billing_month,
                'reading_date': reading_date,
                'issue_date': issue_date,
                'electric_bill_image': image_base64,
                'invoice_date_due': due_date,
                'invoice_line_ids': invoice_lines,
            }

            new_invoice = request.env['account.move'].sudo().create(invoice_vals)

            print(f'Invoice: {new_invoice}')

            if new_invoice:
                new_invoice.sudo().invoice_line_ids[0].write({
                    'previous_reading_unit': new_invoice.previous_reading_unit,
                })

                # Get partner name for success popup
                partner_name = request.env['res.partner'].sudo().browse(partner_id).name

                # FIXED: Redirect with success parameters instead of passing data directly
                return request.redirect(
                    f'/create/electric/bill?success=true&invoice_name={new_invoice.name}&partner_name={partner_name}&meter_id={meter_id}')

        # Handle GET requests, including success case from redirect
        success = request.httprequest.args.get('success') == 'true'
        invoice_name = request.httprequest.args.get('invoice_name', '')
        partner_name = request.httprequest.args.get('partner_name', '')
        meter_id = request.httprequest.args.get('meter_id', '')

        # FIXED: Create success_data from URL parameters instead of POST data
        success_data = None
        if success:
            success_data = {
                'invoice_name': invoice_name,
                'partner_name': partner_name,
                'meter_id': meter_id,
            }

        return request.render('bill_management_system.electric_bill_creation_template_id', {
            'res_partner_list': res_partner_list,
            'success_data': success_data
        })
