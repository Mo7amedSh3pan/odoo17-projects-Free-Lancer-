from odoo import models, fields


class NegativeVisitReasons(models.Model):
    _name = 'visit.negative.reason'
    _description = 'Negative Visit Reasons'

    name = fields.Char(string='Reason ID', required=True)
    description = fields.Text(string='Description')
