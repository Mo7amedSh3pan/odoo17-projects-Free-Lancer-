{
    'name': 'Visit.Management',
    'version': '1.0',
    'category': 'Sales',
    'author': "Sayed Mohamed",
    'depends': ['base', 'sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/visit_management_menus.xml',
        'views/Return_reason_view.xml',
        'views/Nagtive_visit_view.xml'
    ],
    'installable': True,
    'application': True,
}

