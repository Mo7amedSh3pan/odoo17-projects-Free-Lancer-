from odoo import models, fields




class ReturnReasons(models.Model):
    _name = 'visit.return.reason'
    _description = 'Return Reasons'

    reason_id = fields.Char(string='Reason ID', required=True)
    description = fields.Text(string='Description')