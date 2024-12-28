from odoo import models, fields


class employee(models.Model):
    _inherit = 'hr.employee'

    Printer = fields.Char()
    Enable_order_out_of_route = fields.Boolean()
    Default_Replenish_method = fields.Many2one()

    Replenish_Operation_Type = fields.Many2one('stock.picking.type')
    Offloading_Operation_Type = fields.Many2one('stock.picking.type')
    O2C_delivery_Operation_Type = fields.Many2one('stock.picking.type')

    Default_Territory = fields.Many2one('sfa.territory')

    Warehouse = fields.Many2one('stock.location', domain=[
                                ('is_salesman_location', '=', True)])
    Cash_Limit = fields.Integer()

    Van_Number = fields.Many2one('fleet.vehicle')
    Journey_plan_type = fields.Selection([
        ('constant', 'Constant'),
        ('periodic', 'Periodic'),
    ])
