from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class RequestSetLines(models.Model):
    _name = 'request.set.lines'

    request_set = fields.Many2one('request.set')

    name = fields.Char()
    partner_id = fields.Many2one('res.partner', string="Delivery Address")
    salesman = fields.Many2one('hr.employee', string="Salesman")
    picking_type_id = fields.Many2one(
        'stock.picking.type', string="Operation Type")
    location_id = fields.Many2one('stock.location', string="Source Location")
    location_dest_id = fields.Many2one(
        'stock.location', string="Destination Location")
    scheduled_date = fields.Date()
    replenishment_method = fields.Selection([
        ('manual', 'Manual'),
        ('standard template', 'Standard Template'),
        ('customer consumption', 'Customer Consumption'),
        ('salesman target', 'Salesman Target'),
    ])

    standard_template = fields.Many2one('sfa.standard.template')

    target_name = fields.Many2one('sfa.target.definition',
                                  )

    route = fields.Many2one('sfa.journey.assignment',
                            )

    picking_id = fields.Many2one('sfa.rep.request',
                                 string="Related Request",
                                 )

    state = fields.Selection(related='picking_id.state',
                             string='Status', store=True)

    def action_open_request(self):
        self.ensure_one()
        rep_request = self.env['sfa.rep.request'].search(
            [('name', '=', self.name)], limit=1)
        if rep_request:
            return {
                'name': 'Rep Request',
                'type': 'ir.actions.act_window',
                'res_model': 'sfa.rep.request',
                'res_id': rep_request.id,
                'view_mode': 'form',
                'target': 'current',
            }
        return {'type': 'ir.actions.act_window_close'}


class RequestSet(models.Model):
    _name = 'request.set'

    name = fields.Char(string='Reference', required=True,
                       copy=False, readonly=True, default=lambda self: _('New'))

    salesman = fields.Many2many(
        'hr.employee', string="Salesman", required=True)
    request_set_lines = fields.One2many('request.set.lines', 'request_set')
    sfa_rep_request_id = fields.One2many('sfa.rep.request', 'request_set_id')
    created_line_ids = fields.One2many(
        'request.set.lines', 'request_set', string='Created Request Set Lines')
    branch_id = fields.Many2one(
        'res.company', required=True, string='Branch', default=lambda self: self.env.company, domain="[('id', 'in', allowed_company_ids)]")

    scheduled_date = fields.Date(required=True)
    description = fields.Text()
    method_value = fields.Selection([
        ('take default value', 'Take Default Value'),
        ('force method', 'Force Method'),
    ], default='take default value', required=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('rep request', 'Rep Request'),
        ('replenished', 'Replenished'),
        ('submitted', 'Submitted'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    replenishment_method = fields.Selection([
        ('manual', 'Manual'),
        ('standard template', 'Standard Template'),
        ('customer consumption', 'Customer Consumption'),
        ('salesman target', 'Salesman Target'),
    ])
    is_submitted = fields.Boolean(string="Is Submitted", default=False)
    is_replenished = fields.Boolean(default=False)
    is_rep_request = fields.Boolean(default=False)
    is_canceled = fields.Boolean(default=False)


    def unlink(self):
        for record in self:
            if record.state == 'submitted':
                raise UserError(
                    "You cannot delete a record in 'Submitted' state.")
        return super(RepRequest, self).unlink()


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq = self.env['ir.sequence'].next_by_code('request.set')
            if not seq:
                raise UserError(
                    _('Please define a sequence for the Request Set'))
            vals['name'] = seq
        return super(RequestSet, self).create(vals)

    def write(self, vals):
        if 'name' in vals and vals['name'] == _('New'):
            seq = self.env['ir.sequence'].next_by_code('request.set')
            if not seq:
                raise UserError(
                    _('Please define a sequence for the Request Set'))
            vals['name'] = seq
        return super(RequestSet, self).write(vals)

    def create_sfa_rep_request(self, salesman, record):
        sfa_rep_request_obj = self.env['sfa.rep.request']
        request_vals = {
            'salesman': salesman.id,  # Changed from 'salesman' to 'salesman_id'
            # 'request_set': record.id,
            'scheduled_date': record.scheduled_date,
            'picking_type_id': salesman.Replenish_Operation_Type.id,
            'location_id': salesman.Replenish_Operation_Type.default_location_src_id.id if salesman.Replenish_Operation_Type and salesman.Replenish_Operation_Type.default_location_src_id else False,
            'location_dest_id': salesman.Replenish_Operation_Type.default_location_dest_id.id if salesman.Replenish_Operation_Type and salesman.Replenish_Operation_Type.default_location_dest_id else False,
        }

        if record.method_value == 'force method':
            request_vals['replenishment_method'] = record.replenishment_method
        else:
            request_vals['replenishment_method'] = salesman.Default_Replenish_method

        if request_vals['replenishment_method'] == 'standard template':
            request_vals['standard_template'] = salesman.Default_Template.id if salesman.Default_Template else False
        elif request_vals['replenishment_method'] == 'customer consumption':
            request_vals['route'] = salesman.Default_route.id if salesman.Default_route else False
        elif request_vals['replenishment_method'] == 'salesman target':
            request_vals['target_name'] = salesman.Default_Target.id if salesman.Default_Target else False

        return sfa_rep_request_obj.create(request_vals)

    def create_request_set_line(self, record, new_request, salesman):
        request_set_lines_obj = self.env['request.set.lines']
        request_set_line_vals = {
            'request_set': record.id,  # Changed from 'request_set' to 'request_set_id'
            'name': new_request.name,
            # 'partner_id': new_request.partner_id.id if new_request.partner_id else False,
            'salesman': salesman.id,
            'picking_type_id': new_request.picking_type_id.id,
            'location_id': new_request.location_id.id,
            'location_dest_id': new_request.location_dest_id.id,
            'scheduled_date': new_request.scheduled_date,
            'replenishment_method': new_request.replenishment_method,
            'standard_template': new_request.standard_template.id if new_request.standard_template else False,
            'target_name': new_request.target_name.id if new_request.target_name else False,
            'route': new_request.route.id if new_request.route else False,
            'state': new_request.state if new_request.state else False,
            # 'sfa_rep_request_id': new_request.id,
        }
        return request_set_lines_obj.create(request_set_line_vals)

    def action_request(self):

        created_line_ids = []
        for record in self:
            for salesman in record.salesman:
                new_request = self.create_sfa_rep_request(salesman, record)
                new_line = self.create_request_set_line(
                    record, new_request, salesman)
                if new_line:
                    created_line_ids.append(new_line.id)
        self.write({'created_line_ids': [(6, 0, created_line_ids)]})
        self.write({'state': 'rep request'})
        self.is_rep_request = True
        return {'type': 'ir.actions.act_window_close'}

    def action_auto_replenish_lines(self):
        SfaRepRequest = self.env['sfa.rep.request']
        names = self.created_line_ids.mapped('name')
        sfa_rep_requests = SfaRepRequest.search([('name', 'in', names)])
        for request in sfa_rep_requests:
            request.action_auto_replenish()
        self.is_replenished = True
        self.write({'state': 'replenished'})
        return True

    def action_submit_and_create_picking_lines(self):
        SfaRepRequest = self.env['sfa.rep.request']
        names = self.created_line_ids.mapped('name')
        sfa_rep_requests = SfaRepRequest.search([('name', 'in', names)])
        for request in sfa_rep_requests:
            request.action_submit_and_create_picking()
        self.is_submitted = True
        self.state = 'submitted'
        return True

    def action_cancel(self):
        SfaRepRequest = self.env['sfa.rep.request']
        names = self.created_line_ids.mapped('name')
        sfa_rep_requests = SfaRepRequest.search([('name', 'in', names)])
        for request in sfa_rep_requests:
            request.action_cancel()
        self.is_canceled == True
        self.write({'state': 'cancelled'})
