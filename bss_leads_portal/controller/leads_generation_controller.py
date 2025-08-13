import json
import werkzeug.wrappers
from odoo import http
from odoo.http import request
class LeadsGenerationController(http.Controller):
    @http.route('/web/leads/generate', type='http', auth='user', website=True, csrf=True, methods=['GET', 'POST'])
    def generate_leads(self, **kwargs):
        medium_list = []
        medium_recs = request.env['utm.medium'].sudo().search([])
        for rec in medium_recs:
            medium_list.append({'id': rec.id, 'name': rec.name})

        if request.httprequest.method == 'POST':
            contact_name = kwargs.get('contact_name')
            contact_phone = kwargs.get('contact_phone')
            contact_email = kwargs.get('contact_email')
            contact_opportunity = kwargs.get('contact_opportunity')
            description = kwargs.get('description')
            medium_id = kwargs.get('medium_id')
            website = kwargs.get('website')
            tags = kwargs.get('tags')
            split_tags = []

            if isinstance(tags, str):
                tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
                tag_model = request.env['crm.tag'].sudo()

                for tag_name in tag_list:
                    tag = tag_model.search([('name', '=', tag_name)], limit=1)
                    if not tag:
                        tag = tag_model.create({'name': tag_name})
                    split_tags.append(tag.id)

            partner = request.env['res.partner'].sudo().search([
                ('name', '=', contact_name),
                ('phone', '=', contact_phone),
                ('email', '=', contact_email)
            ], limit=1)
            print(f'Partner {partner.name} ---> Found') if partner else None

            if not partner:
                partner = request.env['res.partner'].sudo().create({
                    'name': contact_name,
                    'phone': contact_phone,
                    'email': contact_email,
                })
                print(f'Partner {partner.name} ---> Created')

            # Step 3: Create Lead
            lead_vals = {
                'partner_id': partner.id,
                'email_from': partner.email,
                'phone': partner.phone,
                'name': contact_opportunity,
                'description': description,
                'medium_id': int(medium_id),
                'website': website,
                'type': 'lead',
                'tag_ids': [(6, 0, split_tags)],
            }

            lead = request.env['crm.lead'].sudo().create(lead_vals)
            print(f'Lead Created: {lead.id} for Partner: {partner.id}')

            # Redirect with success parameters
            return request.redirect(f'/web/leads/generate?success=true&lead_name={lead.name}&partner_name={partner.name}')

        # Handle GET requests, including success case from redirect
        success = request.httprequest.args.get('success') == 'true'
        lead_name = request.httprequest.args.get('lead_name', '')
        partner_name = request.httprequest.args.get('partner_name', '')
        return request.render('bss_leads_portal.lead_generation_template', {
            'medium_list': medium_list,
            'success': success,
            'lead_name': lead_name,
            'partner_name': partner_name
        })


