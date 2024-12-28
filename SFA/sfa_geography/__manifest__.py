# File: __manifest__.py

{
    'name': 'SFA.Geography',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Geographical hierarchy for sales',
    'description': """
    This module adds a geographical hierarchy to the Sales application.
    It includes:
    - Regions
    - Stats
    - Cities
    - Areas
    - Territories
    """,
    'author': 'SFA',
    'depends': ['base', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'security/geography_security.xml',
        'views/geography_views.xml',
        'views/menu_items.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
