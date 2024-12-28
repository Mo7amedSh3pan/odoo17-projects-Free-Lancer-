from odoo import models, fields, api


class TargetType(models.Model):
    _name = 'sfa.target.type'
    _description = 'Target Type'

    name = fields.Char(required=True)
    level_of_assignment = fields.Selection([
        ('product', 'Product'),
        ('product category', 'Product Category'),
        ('none', 'None'),
    ], required=True)
    level_of_assignment_is_product = fields.Boolean(
        compute='_compute_level_of_assignment_is_product', store=True)
    level_of_assignment_is_none = fields.Boolean(
        compute='_compute_level_of_assignment_is_product', store=True)

    target_point = fields.Selection([
        ('sO confirm', 'SO Confirm'),
        ('invoice validation', 'Invoice Validation'),
        ('payment', 'Payment'),
        ('delivery validation', 'Delivery Validation'),
    ], required=True)
    target_on = fields.Selection([
        ('amount', 'Amount'),
        ('quantity ', 'Quantity '),
        ('count', 'Count'),
    ], required=True)
    customer_base = fields.Boolean()
    branch_id = fields.Many2one(domain="[('id', 'in', allowed_company_ids)]"
        'res.company', default=lambda self: self.env.company, required=True)

    @api.depends('level_of_assignment')
    def _compute_level_of_assignment_is_product(self):
        for record in self:
            record.level_of_assignment_is_product = record.level_of_assignment == 'product'
            record.level_of_assignment_is_none = record.level_of_assignment in ['product', 'product category']
