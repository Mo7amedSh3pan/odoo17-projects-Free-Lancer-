from odoo import models, fields, api
from datetime import datetime


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    salesman = fields.Many2one('hr.employee', string="Salesman")
    rep_request = fields.Char()
    re = fields.Char()
