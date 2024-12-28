from odoo import models, fields, api


class CustomStockLocation(models.Model):
    _inherit = 'stock.location'

    fleet_ids = fields.One2many('fleet.vehicle', 'Warehouse_id')
    is_van_location = fields.Boolean(string='Is VAN Location', default=False)
    is_salesman_location = fields.Boolean(
        string='Is Salesman Location', default=False)


class CustomFleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    @api.model
    def _get_available_warehouses(self):
        used_warehouses = self.search([]).mapped('Warehouse_id').ids
        return [('id', 'not in', used_warehouses), ('is_van_location', '=', True)]

    Warehouse_id = fields.Many2one(
        'stock.location', domain=_get_available_warehouses)
    capacity_qty = fields.Float(string='Capacity of: Qty')
    capacity_plt = fields.Float(string='Capacity of: PLT')
    capacity_kg = fields.Float(string='Capacity of: Kg')
