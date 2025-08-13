{
    'name': 'bss_payroll_income_tax_slabs',  # Module name
    'author': 'BSS',  # Author name
    'maintainer': 'M.Ahsan Ismail',
    'category': 'BSS',  # Category displayed in info
    'website': 'https://www.bssuniversal.com',  # Website displayed in info
    'depends': ['base', 'hr_payroll', 'hr'],  # Dependencies
    'installable': True,
    'application': True,
    "license": "LGPL-3",
    'data': [
        'security/ir.model.access.csv',
        'wizard/compute_income_tax_wizard_view.xml',
        'data/compute_income_tax_server_action_view.xml',
        'data/tax_slab_2025.xml',
        'views/payroll_income_tax_slab_views.xml',
        'views/hr_contract_inherit_views.xml',
    ], 'images': ['static/description/icon.png'],

}
