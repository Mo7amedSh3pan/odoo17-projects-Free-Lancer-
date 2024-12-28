from odoo import models, fields


class employee(models.Model):
    _inherit = 'hr.employee'

    name = fields.Char()
    Printer = fields.Char()
    Enable_order_out_of_route = fields.Boolean()
    Default_Replenish_method = fields.Selection([
        ('manual', 'Manual'),
        ('standard template', 'Standard Template'),
        ('customer consumption', 'Customer Consumption'),
        ('salesman target', 'Salesman Target'),
    ])

    Replenish_Operation_Type = fields.Many2one('stock.picking.type')
    Offloading_Operation_Type = fields.Many2one('stock.picking.type')
    O2C_delivery_Operation_Type = fields.Many2one('stock.picking.type')

    Default_Territory = fields.Many2one('sfa.territory')
    Default_Template = fields.Many2one('sfa.standard.template')
    Default_Target = fields.Many2one('sfa.target.definition')
    Default_route = fields.Many2one('sfa.journey.assignment', domain=[
                                    ('salesman_id', '=', name)])

    Warehouse = fields.Many2one('stock.location', domain=[
                                ('is_salesman_location', '=', True)])
    Cash_Limit = fields.Integer()

    Van_Number = fields.Many2one('fleet.vehicle')
    Journey_plan_type = fields.Selection([
        ('constant', 'Constant'),
        ('periodic', 'Periodic'),
    ])
