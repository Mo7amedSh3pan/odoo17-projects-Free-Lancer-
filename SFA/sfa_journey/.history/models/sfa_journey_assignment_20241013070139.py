# models/sfa_journey_assignment.py
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SfaJourneyAssignment(models.Model):
    _name = 'sfa.journey.assignment'
    _description = 'SFA Journey Assignment'
    _rec_name = 'journey_id'

    journey_id = fields.Many2one(
        'sfa.journey', string='Journey', required=True, domain="[('branch_id', 'in', allowed_company_ids)]")
    salesman_id = fields.Many2one(
        'hr.employee', string='Salesman', required=True, domain="[('company_id', 'in', allowed_company_ids)]")
    state = fields.Boolean(string='Active', default=True)

    branch_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company, required=True, domain="[('id', 'in', allowed_company_ids)]")

    _sql_constraints = [
        ('unique_active_salesman',
         'UNIQUE(salesman_id)',
         'A salesman cannot be repeat  to multiple journeys.')
    ]

    # @api.constrains('salesman_id', 'state', 'journey_id')
    # def _check_unique_state_salesman(self):
    #     for record in self:
    #         if record.state:
    #             duplicate = self.search([
    #                 ('journey_id', '=', record.journey_id.id),
    #                 ('salesman_id', '=', record.salesman_id.id),
    #                 ('state', '=', True),
    #                 ('id', '!=', record.id)
    #             ])
    #             if duplicate:
    #                 raise ValidationError(
    #                     "A salesman cannot be actively assigned to multiple journeys.")
