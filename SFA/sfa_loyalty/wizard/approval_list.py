from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression

class SFAApprovalList(models.TransientModel):
    _name = 'sfa.approval.list.wizard'
    _description = 'Approval List'


    employee = fields.Many2one('hr.employee')
    required = fields.Boolean()