# File: __manifest__.py

{
    'name': 'SFA.Customer.Update',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Customer hierarchy for sales',
    'author': 'SFA',
    'depends': ['base', 'sale', 'resource', 'sfa_geography'],
    'data': [
        'security/ir.model.access.csv',
        'security/customer_type.xml',
        'security/customer_category.xml',
        'views/customer_update_views.xml',
        'data/week_day_data.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
