from odoo import models, fields


class CustomStockLocation(models.Model):
    _inherit = 'stock.location'

    fleet_id = fields.Many2one('fleet.vehicle')
    is_van_location = fields.Boolean(string='Is VAN Location', default=False)
    is_salesman_location = fields.Boolean(
        string='Is Salesman Location', default=False)


class CustomFleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    Warehouse_ids = fields.Many2one('stock.location')
    capacity_qty = fields.Float(string='Capacity of: Qty')
    capacity_plt = fields.Float(string='Capacity of: PLT')
    capacity_kg = fields.Float(string='Capacity of: Kg')
