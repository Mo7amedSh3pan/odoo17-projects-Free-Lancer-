{
    'name': 'SFA Loyalty',
    'version': '1.0',
    'category': 'Inventory',
    'depends': ['base', 'loyalty','sale','account','mail'],
    'data': [
        'security/ir.model.access.csv',
        'security/sfa_loyalty.xml',
        'wizard/loyalty_generate_wizard_views.xml',
        'wizard/approval_list.xml',
        'views/loyalty_card_views.xml',
        'views/loyalty_mail_views.xml',
        'views/loyalty_reward_views.xml',
        'views/loyalty_rule_views.xml',
        'views/res_partner_views.xml',
        'views/loyalty_views.xml',
        'views/rebate_calculation.xml',
        'views/account_move_view_inherit.xml',
        'data/ir_sequence_data.xml',

    ],



    'installable': True,
    'application': True,
    'auto_install': False,
}
