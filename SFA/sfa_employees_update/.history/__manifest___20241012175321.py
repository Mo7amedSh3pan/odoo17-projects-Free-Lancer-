# File: __manifest__.py

{
    'name': 'SFA.Employees.Update',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Employees hierarchy for sales',
    'author': 'SFA',
    'depends': ['base', 'sale', 'resource',
                'sfa_geography', 'hr', 'stock', 'fleet', 'sfa_replenishment'],
    'data': [
        'views/employee_update_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
