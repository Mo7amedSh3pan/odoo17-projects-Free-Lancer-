# File: __manifest__.py

{
    'name': 'SFA.Update.Van',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Update Inventory ,Fleet modules',
    'author': 'SFA',
    'depends': ['stock', 'fleet'],
    'data': [
        'views/update_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
