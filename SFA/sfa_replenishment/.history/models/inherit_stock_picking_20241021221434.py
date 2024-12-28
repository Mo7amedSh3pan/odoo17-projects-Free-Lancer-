from odoo import models, fields, api
from datetime import datetime


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    salesman = fields.Many2one('hr.employee', string="Salesman")


class StockPickingلإغحث(models.Model):
    _inherit = 'stock.picking'

    salesman = fields.Many2one('hr.employee', string="Salesman")
