{
    'name': 'SFA Replenishment',
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Replenishment methods and standard templates',
    'depends': ['base', 'stock', 'hr', 'sfa_target_management', 'sfa_journey'],
    'data': [
        'views/standard_template_views.xml',
        'views/menu_items.xml',
        'views/inherit_stock_picking.xml',
        'views/rep_request.xml',
        'security/sfa_rules.xml',
        'security/ir.model.access.csv',

    ],



    'installable': True,
    'application': True,
    'auto_install': False,
}
