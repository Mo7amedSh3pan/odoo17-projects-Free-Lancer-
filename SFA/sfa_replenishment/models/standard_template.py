from odoo import models, fields, api


class StandardTemplate(models.Model):
    _name = 'sfa.standard.template'
    _description = 'Standard Template'

    template_id = fields.Char(string='Template ID', required=True)
    name = fields.Char(string='Template Name', required=True)
    state = fields.Boolean(string='Active', default=True)
    branch_id = fields.Many2one(
        'res.company', string='Branch', default=lambda self: self.env.company, domain="[('id', 'in', allowed_company_ids)]")

    company_id = fields.Many2one(
        'res.company', string='Company', required=True, default=lambda self: self.env.company)
    product_ids = fields.One2many(
        'sfa.standard.template.product', 'template_id', string='Products')
    description = fields.Text(string='Description')

    _sql_constraints = [
        ('template_id_unique', 'unique(template_id)', 'Template ID must be unique!')
    ]


class StandardTemplateProduct(models.Model):
    _name = 'sfa.standard.template.product'
    _description = 'Standard Template Product'

    template_id = fields.Many2one('sfa.standard.template', string='Template')
    product_id = fields.Many2one(
        'product.product', string='Product', required=True,
        domain="['|',('company_id', 'in', allowed_company_ids),('company_id', '=', False)]"
    )
    quantity = fields.Integer(string='Quantity', required=True)
    uom_id = fields.Many2one('uom.uom', string='UOM', required=True)
    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.company)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id
