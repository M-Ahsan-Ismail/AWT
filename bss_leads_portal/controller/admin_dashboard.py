from odoo import http, fields
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class AdminDashboard(http.Controller):

    @http.route('/admin/leads/dashboard', type='http', auth="user", website=True, csrf=False, methods=['GET'])
    def leads_dashboard(self, **kwargs):
        try:
            # Get all users for the dropdown
            res_users = request.env['res.users'].sudo().search_read([], ['id', 'name'])

            # Build domain based on filters
            domain = []

            start_date = kwargs.get('start_date')
            end_date = kwargs.get('end_date')
            sales_person = kwargs.get('sales_person')
            lead_type = kwargs.get('type')

            # Debug logging
            _logger.info("Filter parameters: %s", kwargs)

            # Add date filters
            if start_date:
                try:
                    domain.append(('create_date', '>=', start_date + ' 00:00:00'))
                except:
                    pass

            if end_date:
                try:
                    domain.append(('create_date', '<=', end_date + ' 23:59:59'))
                except:
                    pass

            # Add salesperson filter
            if sales_person:
                try:
                    domain.append(('user_id', '=', int(sales_person)))
                except ValueError:
                    pass

            # Add type filter
            if lead_type in ['lead', 'opportunity']:
                domain.append(('type', '=', lead_type))

            _logger.info("Search domain: %s", domain)

            # Search for leads/opportunities
            leads = request.env['crm.lead'].sudo().search(domain, order='create_date desc')

            _logger.info("Found %d records", len(leads))

            # Process data
            lead_data = []
            for lead in leads:
                try:
                    # Handle partner image safely
                    image_data = None
                    if lead.partner_id and lead.partner_id.image_1920:
                        try:
                            if isinstance(lead.partner_id.image_1920, bytes):
                                image_data = lead.partner_id.image_1920.decode('utf-8')
                            else:
                                image_data = str(lead.partner_id.image_1920)
                        except:
                            image_data = None

                    lead_data.append({
                        'id': lead.id,
                        'name': lead.name or 'N/A',
                        'description': lead.description or 'No description',
                        'expected_revenue': lead.expected_revenue or 0.0,
                        'type': lead.type,
                        'partner_name': lead.partner_id.name if lead.partner_id else 'No Contact',
                        'image': image_data,
                        'stage': lead.stage_id.name if lead.stage_id else 'New',
                        'create_date': lead.create_date,
                    })
                except Exception as e:
                    _logger.error("Error processing lead %s: %s", lead.id, str(e))
                    continue

            return request.render('bss_leads_portal.crm_leads_admin_dashboard_id', {
                'res_users': res_users,
                'leads_opportunity_list': lead_data,
                'kwargs': kwargs,
            })

        except Exception as e:
            _logger.error("Dashboard error: %s", str(e))
            return request.render('bss_leads_portal.crm_leads_admin_dashboard_id', {
                'res_users': [],
                'leads_opportunity_list': [],
                'kwargs': kwargs,
                'error_message': str(e),
            })
