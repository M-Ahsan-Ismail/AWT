{
    'name': 'bss_leads_portal',  # Module name
    'author': 'BSS',  # Author name
    'maintainer': 'M.Ahsan Ismail',
    'developer_portfolio': 'https://ahsan-developer.netlify.app/',
    'category': 'BSS',  # Category displayed in info
    'website': 'https://www.bssuniversal.com',  # Website displayed in info
    'depends': ['base', 'crm', 'portal', 'website'],  # Dependencies
    'installable': True,
    'application': True,
    "license": "LGPL-3",
    'data': [
        'views/lead_generation_controller_view.xml',
        'views/dealer_dashboard_portal.xml',

    ], 'images': ['static/description/icon.png'],

}
