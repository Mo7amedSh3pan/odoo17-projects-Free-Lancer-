from odoo import models, fields




class ReturnReasons(models.Model):
    _name = 'visit.return.reason'
    _description = 'Return Reasons'

    name = fields.Char(string='Reason ID', required=True)
    description = fields.Text(string='Description')