from odoo import models, fields


class CustomStockLocation(models.Model):
    _inherit = 'stock.location'

    is_van_location = fields.Boolean(string='Is VAN Location', default=False)
    is_salesman_location = fields.Boolean(
        string='Is Salesman Location', default=False)
