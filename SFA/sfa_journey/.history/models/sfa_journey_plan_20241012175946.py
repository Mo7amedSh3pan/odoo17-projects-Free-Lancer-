# models/sfa_journey_plan.py
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SfaJourneyPlan(models.Model):
    _name = 'sfa.journey.plan'
    _description = 'SFA Journey Plan'
    
    

    journey_id = fields.Many2one(
        'sfa.journey', string='Journey', required=True, domain="[('branch_id', 'in', allowed_company_ids)]")
    sequence = fields.Integer(string='Sequence', default=1)
    customer_id = fields.Many2one(
        'res.partner', string='Customer', required=True,
        domain="[('company_id', 'in', allowed_company_ids),('customer_rank', '>', 0)]"
    )
    user = fields.Many2one('res.users', string='User',
                           default=lambda self: self.env.user)
    branch_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company, required=True, domain="[('id', 'in', allowed_company_ids)]")

    @api.model
    def _get_customer_domain(self):
        return [('company_id', '=', self.env.company.id)]

    visit_frequency = fields.Integer(string='Visit Frequency')
    week = fields.Selection([
        ('W1', 'Week 1'),
        ('W2', 'Week 2'),
        ('W3', 'Week 3'),
        ('W4', 'Week 4')
    ], string='Week', required=True)
    sat = fields.Boolean(string='Saturday')
    sun = fields.Boolean(string='Sunday')
    mon = fields.Boolean(string='Monday')
    tue = fields.Boolean(string='Tuesday')
    wed = fields.Boolean(string='Wednesday')
    thu = fields.Boolean(string='Thursday')
    fri = fields.Boolean(string='Friday')

    @api.constrains('customer_id', 'week')
    def _check_unique_customer_week(self):
        for record in self:
            duplicate = self.search([
                ('customer_id', '=', record.customer_id.id),
                ('week', '=', record.week),
                ('journey_id', '=', record.journey_id.id),
                ('id', '!=', record.id)
            ])
            if duplicate:
                raise ValidationError(
                    "A customer cannot be assigned to the same week more than once within a journey.")
