# File: __manifest__.py

{
    'name': 'SFA Supervisor Secure',
    'version': '1.0',
    'category': 'Sales',
    # 'summary': 'Update Inventory ,Fleet modules',
    'author': 'SFA',
    'depends': ['stock', 'fleet', 'sfa_replenishment', 'sfa_request_set','sale','account','point_of_sale','spreadsheet_dashboard'],
    'data': [
        'views/res_users_inherit_view.xml',
        'views/account_move_inherit_view.xml',
        'views/pos_dashboard.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
