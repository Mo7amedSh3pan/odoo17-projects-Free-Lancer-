from odoo import models, fields


class CustomStockLocation(models.Model):
    _inherit = 'stock.location'

    is_van_location = fields.Boolean(string='Is VAN Location', default=False)
    is_salesman_location = fields.Boolean(
        string='Is Salesman Location', default=False)


class CustomFleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    Warehouse_ids = fields.One2many('stock.location', 'fleet_id')
    capacity_qty = fields.Float(string='Capacity of: Qty')
    capacity_plt = fields.Float(string='Capacity of: PLT')
    capacity_kg = fields.Float(string='Capacity of: Kg')
