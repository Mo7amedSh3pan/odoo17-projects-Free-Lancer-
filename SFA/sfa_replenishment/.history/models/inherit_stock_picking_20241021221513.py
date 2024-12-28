from odoo import models, fields, api
from datetime import datetime


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    salesman = fields.Many2one('hr.employee', string="Salesman")


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    otype = fields.Many2one('hr.employee', string="Otype")
