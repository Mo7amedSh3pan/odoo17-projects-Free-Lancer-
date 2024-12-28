# models/res_users.py
from odoo import models, fields, api


class ResUsersInherit(models.Model):
    _inherit = 'res.users'

    sales_manager = fields.Boolean(string='Sales Manager')
