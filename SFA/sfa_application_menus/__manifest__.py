# File: __manifest__.py

{
    'name': 'SFA Application Menus',
    'version': '1.0',
    'category': 'Sales',
    'author': 'SFA',
    'depends': ['base', 'sale','om_account_accountant'],
    'data': [
        'views/create_edit_root_menus.xml',
        'views/dashboards_menus.xml',
        'views/customers_menus.xml',
        'views/follow_up_menus.xml',
        'views/reports_menus.xml',
        'views/configurations_menus.xml',
        'views/vendors_menus.xml',
        'views/accounting_manus.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
