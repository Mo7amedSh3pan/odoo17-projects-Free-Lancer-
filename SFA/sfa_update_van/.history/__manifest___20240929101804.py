# File: __manifest__.py

{
    'name': 'SFA.Update',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Geographical hierarchy for sales',
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
