# models/sfa_journey_assignment.py
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date


class SfaJourneyAssignment(models.Model):
    _name = 'sfa.journey.assignment'
    _description = 'SFA Journey Assignment'
    _rec_name = 'journey_id'

    journey_id = fields.Many2one(
        'sfa.journey', string='Journey', required=True, domain="[('branch_id', 'in', allowed_company_ids)]")
    salesman_id = fields.Many2one(
        'hr.employee', string='Salesman', required=True, domain="[('company_id', 'in', allowed_company_ids)]")
    state = fields.Boolean(string='Active', default=True)

    start_date = fields.Date()
    end_date = fields.Date()

    branch_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company, required=True, domain="[('id', 'in', allowed_company_ids)]")

    _sql_constraints = [
        ('unique_active_salesman',
         'UNIQUE(salesman_id,journey_id)',
         'A salesman cannot be exist in more than one line.')
    ]

    @api.constrains('start_date', 'end_date')
    def _check_date_order(self):
        for record in self:
            if record.start_date and record.end_date and record.start_date > record.end_date:
                raise ValidationError(                    _("The start date must be before the end date."))
