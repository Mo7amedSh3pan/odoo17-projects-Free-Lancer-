# models/sfa_journey.py
from odoo import models, fields, api


class SfaJourney(models.Model):
    _name = 'sfa.journey'
    _description = 'SFA Journey'

    route_id = fields.Char(string='Reference', required='True')
    name = fields.Char(string='Route Name', required='True')
    description = fields.Text(string='Description')
    state = fields.Boolean(string='Active', default=True)

    branch_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company, required=True, domain="[('id', 'in', allowed_company_ids)]")

    plan_ids = fields.One2many(
        'sfa.journey.plan', 'journey_id', string='Plans')
    assignment_ids = fields.One2many(
        'sfa.journey.assignment', 'journey_id', string='Assignments')

    _sql_constraints = [
        ('unique_route_id', 'UNIQUE(route_id,branch_id)',
         'This Reference with this Branch must be unique!')
    ]
    # ('unique_name', 'UNIQUE(name)', 'The Route Name must be unique!'

    def action_view_journey_plans(self):
        self.ensure_one()
        return {
            'name': 'Journey Plans',
            'type': 'ir.actions.act_window',
            'res_model': 'sfa.journey.plan',
            'view_mode': 'tree',
            'view_id': self.env.ref('sfa_journey.view_sfa_journey_plan_tree_without_journey_id').id,
            'domain': [('journey_id', '=', self.id)],
            'context': {'default_journey_id': self.id},
        }

    def action_view_journey_assignments(self):
        self.ensure_one()
        return {
            'name': 'Journey assignments',
            'type': 'ir.actions.act_window',
            'res_model': 'sfa.journey.assignment',
            'view_mode': 'tree',
            'view_id': self.env.ref('sfa_journey.view_sfa_journey_assignment_tree_without_journey_id').id,
            'domain': [('journey_id', '=', self.id)],
            'context': {'default_journey_id': self.id},
        }
