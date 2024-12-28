from odoo import models, fields, api
from odoo.exceptions import ValidationError
from lxml import etree


class TargetProductLine(models.Model):
    _name = 'sfa.target.product.line'
    _description = 'Target Product Line'

    product_category_id = fields.Many2one(
        'product.category'
    )
    product_id = fields.Many2one(
        'product.product')
    customer_id = fields.Many2one(
        'res.partner', domain=[('customer_rank', '>', 0)])
    target_id = fields.Many2one(
        'sfa.target.definition')
    uom_id = fields.Many2one('uom.uom', string='UOM', required=True, )


domain = [
    ('category_id', '=', product_uom_category_id)]
    target = fields.Integer()
    is_customer_editable = fields.Boolean(readonly=True, compute='_compute_is_customer_editable',
                                          store=True)

    product_editable = fields.Boolean(readonly=True, compute='_compute_product_editable',
                                      store=True)

    product_category_id_editable = fields.Boolean(readonly=True, compute='_compute_product_category_id_editable',
                                                  store=True)

    @ api.depends('target_id', 'target_id.target_type_id', 'target_id.customer_base_checked')
    def _compute_is_customer_editable(self):
        for record in self:
            if record.target_id:
                record.is_customer_editable = record.target_id.customer_base_checked
                if not record.is_customer_editable:
                    record.customer_id = False
            else:
                record.is_customer_editable = False

    @ api.depends('target_id', 'target_id.target_type_id', 'target_id.level_of_assignment_is_product_definition')
    def _compute_product_editable(self):
        for record in self:
            if record.target_id:
                record.product_editable = record.target_id.level_of_assignment_is_product_definition
                if not record.product_editable:
                    record.product_id = False
            else:
                record.product_editable = False

    @ api.depends('target_id', 'target_id.target_type_id', 'target_id.level_of_assignment_is_none_definition')
    def _compute_product_category_id_editable(self):
        for record in self:
            if record.target_id:
                record.product_category_id_editable = record.target_id.level_of_assignment_is_none_definition
                if not record.product_category_id_editable:
                    record.product_category_id = False
            else:
                record.product_category_id_editable = False
