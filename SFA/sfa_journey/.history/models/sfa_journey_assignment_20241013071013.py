# models/sfa_journey_assignment.py
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from date


class SfaJourneyAssignment(models.Model):
    _name = 'sfa.journey.assignment'
    _description = 'SFA Journey Assignment'
    _rec_name = 'journey_id'

    journey_id = fields.Many2one(
        'sfa.journey', string='Journey', required=True, domain="[('branch_id', 'in', allowed_company_ids)]")
    salesman_id = fields.Many2one(
        'hr.employee', string='Salesman', required=True, domain="[('company_id', 'in', allowed_company_ids)]")
    state = fields.Boolean(string='Active', default=True)

    start_date = Date()

    branch_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company, required=True, domain="[('id', 'in', allowed_company_ids)]")

    _sql_constraints = [
        ('unique_active_salesman',
         'UNIQUE(salesman_id,journey_id)',
         'A salesman cannot be exist in more than one line.')
    ]
