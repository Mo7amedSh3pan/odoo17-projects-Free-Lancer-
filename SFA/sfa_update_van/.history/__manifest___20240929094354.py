# File: __manifest__.py

{
    'name': 'SFA.Update',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Geographical hierarchy for sales',
    'author': 'SFA',
    'depends': ['stock'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/update_views.xml',
        # 'views/menu_items.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
