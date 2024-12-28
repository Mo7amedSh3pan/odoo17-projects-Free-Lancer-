# File: __manifest__.py

{
    'name': 'SFA.Target.Management',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Target Management',

    'author': 'SFA',
    'depends': ['base', 'hr', 'product', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'security/sfa_target_type.xml',
        'views/target_type_views.xml',
        'views/target_definition_views.xml',
    ],

    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
