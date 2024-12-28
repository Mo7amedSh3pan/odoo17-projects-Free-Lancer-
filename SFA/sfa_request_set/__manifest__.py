{
    'name': 'SFA Request Set',
    'version': '1.0',
    'category': 'Inventory',
    'depends': ['base', 'stock', 'hr', 'sfa_target_management', 'sfa_journey', 'sfa_replenishment'],
    'data': [
        'security/ir.model.access.csv',
        'security/request_set.xml',
        'views/request_set_views.xml',
        'data/ir_sequence_data.xml',
    ],



    'installable': True,
    'application': True,
    'auto_install': False,
}
