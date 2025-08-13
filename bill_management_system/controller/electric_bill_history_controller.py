from odoo import http
from odoo.http import request
from datetime import datetime
import logging
import base64

_logger = logging.getLogger(__name__)


class ViewBillHistory(http.Controller):
    @http.route('/bill/history', type='http', auth="user", website=True, csrf=False, methods=['GET', 'POST'])
    def bill_history(self, **kw):
        try:
            meter_id = kw.get('meter_id', '').strip()
            from_date = kw.get('from_date', '').strip()
            to_date = kw.get('to_date', '').strip()

            # Phase 1: Show form to enter meter_id only
            if not meter_id:
                return request.render('bill_management_system.bill_history_template_id', {
                    'phase': 'ask_meter',
                })

            # Phase 2: Meter ID is provided, allow date filtering
            domain = [('is_bill', '=', True), ('meter_id', '=', meter_id)]

            # Add date filters if provided
            if from_date:
                try:
                    from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
                    domain.append(('billing_month', '>=', from_date_obj))
                except ValueError:
                    _logger.warning(f"Invalid from_date format: {from_date}")

            if to_date:
                try:
                    to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
                    domain.append(('billing_month', '<=', to_date_obj))
                except ValueError:
                    _logger.warning(f"Invalid to_date format: {to_date}")

            # Search for bills with error handling
            try:
                bill_recs = request.env['account.move'].with_context(active_test=False).sudo().search(
                    domain, order='billing_month desc')
            except Exception as e:
                _logger.error(f"Error searching bills: {str(e)}")
                bill_recs = request.env['account.move']

            # Process bill records
            bill_history_list = []
            for rec in bill_recs:
                try:
                    # Handle meter and partner image safely
                    meter_image = None
                    partner_image = None
                    if rec.electric_bill_image:
                        if isinstance(rec.electric_bill_image, bytes):
                            # Convert base64 bytes to data URL
                            meter_image = f"data:image/jpeg;base64,{rec.electric_bill_image.decode('utf-8')}"
                        else:
                            # Assume it's already base64 string
                            meter_image = f"data:image/jpeg;base64,{rec.electric_bill_image}"
                        meter_image = None

                    if rec.partner_id.image_1920:
                        partner_image = rec.partner_id.image_1920
                        if partner_image and isinstance(partner_image, bytes):
                            partner_image = partner_image.decode('utf-8')
                        else:
                            partner_image = None

                    # Format dates safely
                    invoice_date_str = "N/A"
                    if rec.invoice_date:
                        try:
                            invoice_date_str = rec.invoice_date.strftime("%Y-%m-%d")
                        except:
                            invoice_date_str = str(rec.invoice_date)

                    billing_month_str = "N/A"
                    if rec.billing_month:
                        try:
                            billing_month_str = rec.billing_month.strftime("%Y-%m-%d")
                        except:
                            billing_month_str = str(rec.billing_month)

                    bill_history_list.append({
                        'id': rec.id,
                        'name': rec.name or 'N/A',
                        'invoice_date': invoice_date_str,
                        'billing_month': billing_month_str,
                        'meter_id': rec.meter_id or 'N/A',
                        'customer_name': rec.partner_id.name if rec.partner_id else 'N/A',
                        'total_bill_amount': rec.amount_total or 0.0,
                        'meter_image': meter_image,
                        'partner_image': partner_image,
                        'state': rec.state or 'draft',
                        'paid': True if rec.amount_residual == 0.0 else False,
                    })

                except Exception as rec_error:
                    _logger.error(f"Error processing bill record {rec.id}: {str(rec_error)}")
                    continue

            return request.render('bill_management_system.bill_history_template_id', {
                'phase': 'show_filter_and_results',
                'meter_id': meter_id,
                'from_date': from_date,
                'to_date': to_date,
                'bill_history_list': bill_history_list,
            })

        except Exception as e:
            _logger.error(f"Error in bill_history controller: {str(e)}")
            return request.render('bill_management_system.bill_history_template_id', {
                'phase': 'ask_meter',
                'error_message': 'An error occurred while processing your request. Please try again.',
            })

    @http.route('/bill/details/<int:bill_id>', type='http', auth="user", website=True)
    def view_bill_details(self, bill_id, **kw):
        try:
            bill = request.env['account.move'].sudo().browse(bill_id)
            if not bill.exists():
                return request.render('bill_management_system.bill_details_template', {
                    'bill': None
                })

            # Handle meter image
            meter_image = None
            if bill.electric_bill_image:
                try:
                    if isinstance(bill.electric_bill_image, bytes):
                        # Convert base64 bytes to data URL
                        meter_image = f"data:image/jpeg;base64,{bill.electric_bill_image.decode('utf-8')}"
                    else:
                        # Assume it's already base64 string
                        meter_image = f"data:image/jpeg;base64,{bill.electric_bill_image}"
                except Exception as e:
                    _logger.error(f"Error processing image for bill {bill.id}: {str(e)}")
                    meter_image = None

            bill_data = {
                'id': bill.id,
                'name': bill.name or 'N/A',
                'customer_name': bill.partner_id.name if bill.partner_id else 'N/A',
                'meter_id': bill.meter_id or 'N/A',
                'invoice_date': bill.invoice_date.strftime("%Y-%m-%d") if bill.invoice_date else "N/A",
                'billing_month': bill.billing_month.strftime("%Y-%m-%d") if bill.billing_month else "N/A",
                'total_bill_amount': bill.amount_total or 0.0,
                'state': bill.state or 'draft',
                'meter_image': meter_image,
            }
            return request.render('bill_management_system.bill_details_template', {
                'bill': bill_data
            })
        except Exception as e:
            _logger.error(f"Error rendering bill details: {str(e)}")
            return request.render('bill_management_system.bill_details_template', {
                'bill': None
            })

    @http.route('/bill/pdf/<int:bill_id>', type='http', auth="user", website=True)
    def download_bill_pdf(self, bill_id, **kw):
        try:
            bill = request.env['account.move'].sudo().browse(bill_id)
            if not bill.exists():
                return request.not_found()

            # STEP 1 — Find the custom bill report
            report = request.env['ir.actions.report'].search(
                [('report_name', '=', 'bill_management_system.report_lesco_bill_template')],
                # <-- replace with your report's technical name
                limit=1
            )
            if not report:
                _logger.error("Bill report not found for account.move.")
                return request.not_found()

            # STEP 2 — Render PDF
            pdf_content = report._render_qweb_pdf(report.report_name, res_ids=[bill.id])[0]
            if not pdf_content:
                _logger.error(f"PDF content empty for Bill {bill.id}")
                return request.not_found()

            # STEP 3 — Store PDF in ir.attachment
            attachment = request.env['ir.attachment'].sudo().create({
                'name': f'Bill_{bill.name or str(bill.id)}.pdf',
                'type': 'binary',
                'datas': base64.b64encode(pdf_content),
                'res_model': 'account.move',
                'res_id': bill.id,
                'mimetype': 'application/pdf',
            })

            # STEP 4 — Return PDF as download
            return request.make_response(pdf_content, headers=[
                ('Content-Type', 'application/pdf'),
                ('Content-Length', len(pdf_content)),
                ('Content-Disposition', f'attachment; filename=Bill_{bill.name or bill.id}.pdf')
            ])

        except Exception as e:
            _logger.error(f"Error generating bill PDF: {str(e)}")
            return request.not_found()

# from odoo import http
# from odoo.http import request
# from datetime import datetime
#
# class ViewBillHistory(http.Controller):
#     @http.route('/bill/history', type='http', auth="user", website=True, csrf=False, methods=['GET', 'POST'])
#     def bill_history(self, **kw):
#         meter_id = kw.get('meter_id')
#         from_date = kw.get('from_date')
#         to_date = kw.get('to_date')
#
#         bill_history_list = []
#
#         if not meter_id:
#             # Phase 1: Show form to enter meter_id only
#             return request.render('bill_management_system.bill_history_template_id', {
#                 'phase': 'ask_meter',
#             })
#
#         # Phase 2: Meter ID is provided, allow date filtering
#         domain = [('is_bill', '=', True), ('meter_id', '=', meter_id)]
#
#         if from_date:
#             domain.append(('billing_month', '>=', from_date))
#         if to_date:
#             domain.append(('billing_month', '<=', to_date))
#
#         bill_recs = request.env['account.move'].with_context(active_test=False).sudo().search(
#             domain, order='billing_month desc')
#
#         for rec in bill_recs:
#             meter_image = rec.electric_bill_image
#             meter_image = meter_image.decode('utf-8') if meter_image else None
#
#             bill_history_list.append({
#                 'id': rec.id,
#                 'name': rec.name or 'N/A',
#                 'invoice_date': rec.invoice_date.strftime("%Y-%m-%d") if rec.invoice_date else "N/A",
#                 'billing_month': rec.billing_month.strftime("%Y-%m-%d") if rec.billing_month else "N/A",
#                 'meter_id': rec.meter_id or 'N/A',
#                 'customer_name': rec.partner_id.name if rec.partner_id else 'N/A',
#                 'total_bill_amount': rec.amount_total or 0.0,
#                 'meter_image': meter_image,
#             })
#
#         return request.render('bill_management_system.bill_history_template_id', {
#             'phase': 'show_filter_and_results',
#             'meter_id': meter_id,
#             'from_date': from_date,
#             'to_date': to_date,
#             'bill_history_list': bill_history_list,
#         })
