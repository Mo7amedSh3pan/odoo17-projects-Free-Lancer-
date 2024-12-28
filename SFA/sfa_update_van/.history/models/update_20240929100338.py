from odoo import models, fields


class CustomStockLocation(models.Model):
    _inherit = 'stock.location'

    fleet_ids = fields.One2many('fleet.vehicle')
    is_van_location = fields.Boolean(string='Is VAN Location', default=False)
    is_salesman_location = fields.Boolean(
        string='Is Salesman Location', default=False)


class CustomFleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    Warehouse_id = fields.Many2one('stock.location', domain=[
                                   ('is_van_location', '=', True)])
    capacity_qty = fields.Float(string='Capacity of: Qty')
    capacity_plt = fields.Float(string='Capacity of: PLT')
    capacity_kg = fields.Float(string='Capacity of: Kg')
