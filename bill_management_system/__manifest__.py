{
    'name': 'bill_management_system',  # Module name
    'author': 'M.Ahsan',  # Author name
    'maintainer': 'M.Rizwan',
    'category': 'BSS',  # Category displayed in info
    'website': 'https://ahsan-developer.netlify.app',  # Website displayed in info
    'depends': ['base', 'sale', 'sale_subscription', 'account', 'account_accountant','website','portal'],  # Dependencies
    'installable': True,
    'application': True,
    "license": "LGPL-3",
    'data': [
        # 'security/ir.model.access.csv',
        'report/ebill_report_temp.xml',
        'views/invoice_inherit_views.xml',
        'views/res_partner_inherit_views.xml',
        'views/electric_bill_controller_views.xml',
        'views/electric_bill_history_controller_view.xml',
    ], 'images': ['static/description/icon.png'],

}
