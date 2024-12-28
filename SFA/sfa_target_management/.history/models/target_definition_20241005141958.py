from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TargetDefinition(models.Model):
    _name = 'sfa.target.definition'
    _description = 'Target Definition'

    name = fields.Char(string="Target Name", required=True)
    salesman_id = fields.Many2one('hr.employee', required=True)
    target_type_id = fields.Many2one(
        'sfa.target.type', required=True
    )

    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    period_display = fields.Char(
        string="Period", compute="_compute_period_display", store=True)
    branch_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company, required=True)

    product_lines = fields.One2many(
        'sfa.target.product.line', 'target_id')

    level_of_assignment_is_product_definition = fields.Boolean(
        compute='_compute_level_of_assignment_is_product_definition', store=True)
    level_of_assignment_is_none_definition = fields.Boolean(
        compute='_compute_level_of_assignment_is_none_definition', store=True)
    customer_base_checked = fields.Boolean(
        compute='_compute_customer_base_checked', store=True)

    _sql_constraints = [
        ('check_same_month_year',
         'CHECK(EXTRACT(YEAR FROM date_from) = EXTRACT(YEAR FROM date_to) AND EXTRACT(MONTH FROM date_from) = EXTRACT(MONTH FROM date_to))',
         'The Date From and Date To must be in the same month and year.')
    ]

    @api.constrains('date_from', 'date_to')
    def _check_date_range(self):
        for record in self:
            if record.date_from and record.date_to:
                if record.date_from > record.date_to:
                    raise ValidationError(
                        "The Start Date must be less than or equal to the End Date.")

    @api.depends('target_type_id', 'target_type_id.level_of_assignment')
    def _compute_level_of_assignment_is_product_definition(self):
        for record in self:
            if record.target_type_id:
                record.level_of_assignment_is_product_definition = record.target_type_id.level_of_assignment_is_product
            else:
                record.level_of_assignment_is_product_definition = False

    @api.depends('target_type_id', 'target_type_id.level_of_assignment_is_none')
    def _compute_level_of_assignment_is_none_definition(self):
        for record in self:
            if record.target_type_id:
                record.level_of_assignment_is_none_definition = record.target_type_id.level_of_assignment_is_none
            else:
                record.level_of_assignment_is_none_definition = False

    @api.depends('target_type_id', 'target_type_id.customer_base')
    def _compute_customer_base_checked(self):
        for record in self:
            if record.target_type_id:
                record.customer_base_checked = record.target_type_id.customer_base
            else:
                record.customer_base_checked = False

    @api.depends('date_from')
    def _compute_period_display(self):
        for record in self:
            if record.date_from:
                record.period_display = record.date_from.strftime('%B %Y')
            else:
                record.period_display = False

    @api.constrains('salesman_id', 'target_type_id', 'period_display')
    def _check_unique_target(self):
        for record in self:
            domain = [
                ('salesman_id', '=', record.salesman_id.id),
                ('target_type_id', '=', record.target_type_id.id),
                ('period_display', '=', record.period_display),
                ('id', '!=', record.id)  # Exclude the current record
            ]
            if self.search_count(domain) > 0:
                raise ValidationError(
                    "A target with the same Salesman, Target Type, and Period already exists.")
