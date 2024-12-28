# __manifest__.py
{
    'name': 'SFA Journey',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Sales Force Automation Journey Management',
    'depends': ['base', 'hr', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'security/sfa_target_type.xml',
        'views/sfa_journey_views.xml',
        'views/sfa_journey_plan_views.xml',
        'views/sfa_journey_assignment_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
