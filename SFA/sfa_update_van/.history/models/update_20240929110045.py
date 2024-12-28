from odoo import models, fields, api


class CustomStockLocation(models.Model):
    _inherit = 'stock.location'

    # fleet_ids = fields.One2many('fleet.vehicle', 'Warehouse_id')
    is_van_location = fields.Boolean(string='Is VAN Location', default=False)
    is_salesman_location = fields.Boolean(
        string='Is Salesman Location', default=False)


class CustomFleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    @api.depends('Warehouse_id')
    def _compute_warehouse_domain(self):
        used_warehouses = self.search([]).mapped('Warehouse_id').ids
        domain = [('id', 'not in', used_warehouses),
                  ('is_van_location', '=', True)]
        return domain

    Warehouse_id = fields.Many2one(
        'stock.location', compute='_compute_warehouse_id', inverse='_inverse_warehouse_id', store=True)

    @api.depends()
    def _compute_warehouse_id(self):
        for record in self:
            if not record.Warehouse_id:
                domain = self._compute_warehouse_domain()
                available_warehouses = self.env['stock.location'].search(
                    domain)
                if available_warehouses:
                    record.Warehouse_id = available_warehouses[0]

    def _inverse_warehouse_id(self):
        for record in self:
            record.Warehouse_id = record.Warehouse_id

    capacity_qty = fields.Float(string='Capacity of: Qty')
    capacity_plt = fields.Float(string='Capacity of: PLT')
    capacity_kg = fields.Float(string='Capacity of: Kg')
