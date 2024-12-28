from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError


class ProductLines(models.Model):
    _name = 'product.lines'
    _description = 'Product Lines'

    rep_request_id = fields.Many2one('sfa.rep.request')

    product_id = fields.Many2one('product.product')
    product_uom = fields.Many2one('uom.uom', string='Unit')
    product_uom_qty = fields.Float(string='Demand')
    description = fields.Text()
    date = fields.Datetime(string="Scheduled Date")
    date_deadline = fields.Datetime(string="Deadline")


class RepRequest(models.Model):
    _name = 'sfa.rep.request'
    _description = 'Replenishment Request'

    name = fields.Char(string='Reference')
    temp_name = fields.Char(string='Temporary Reference', copy=False)

    request_set_id = fields.Many2many('request.set')
    product_line_ids = fields.One2many('product.lines', "rep_request_id")
    salesman = fields.Many2one('hr.employee', string="Salesman")
    replenishment_method = fields.Selection([
        ('manual', 'Manual'),
        ('standard template', 'Standard Template'),
        ('customer consumption', 'Customer Consumption'),
        ('salesman target', 'Salesman Target'),
    ])

    branch_id = fields.Many2one(
        'res.company', string='Branch', default=lambda self: self.env.company)
    company_id = fields.Many2one(
        'res.company', string='Company', required=True, default=lambda self: self.env.company)

    is_submitted = fields.Boolean(string="Is Submitted", default=False)
    type = fields.Char(string="Is Submitted", default=False)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('replenished', 'Replenished'),
        ('submitted', 'Submitted'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    auto_replenish_done = fields.Boolean(
        string="Auto Replenish Done", default=False)  # field to track button click
    standard_template = fields.Many2one('sfa.standard.template')
    location_id = fields.Many2one(
        'stock.location', string="Source Location", compute='_compute_location_id', readonly=True)
    #
    location_dest_id = fields.Many2one(
        'stock.location', string="Destination Location", compute='_compute_location_dest_id', readonly=True)
    #
    scheduled_date = fields.Datetime(default=fields.Datetime.now)
    origin = fields.Char(string="Source Document")
    route = fields.Many2one('sfa.journey.assignment',
                            domain="[('id', 'in', allowed_route_ids)]")
    period = fields.Char(
        string="Period", compute="_compute_period", store=True)
    target_name = fields.Many2one(
        'sfa.target.definition', domain="[('salesman_id', '=', salesman),('period_display', '=', period)]")

    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',
        required=False, readonly=True,
        compute='_compute_picking_type_id', store=True, default=False)

    @api.model
    def create(self, vals):
        if vals.get('temp_name'):
            vals['name'] = vals.pop('temp_name')
        elif not vals.get('name'):
            vals['name'] = self._get_new_name(vals.get('picking_type_id'))
        return super(RepRequest, self).create(vals)

    def write(self, vals):
        if 'picking_type_id' in vals and self.state == 'draft':
            if vals.get('temp_name'):
                vals['name'] = vals.pop('temp_name')
            else:
                vals['name'] = self._get_new_name(vals['picking_type_id'])
        return super(RepRequest, self).write(vals)

    @api.onchange('picking_type_id')
    def _onchange_picking_type_id(self):
        if self.picking_type_id and self.state == 'draft':
            self.temp_name = self._get_new_name(self.picking_type_id.id)

    def _get_new_name(self, picking_type_id):
        picking_type = self.env['stock.picking.type'].browse(picking_type_id)
        if picking_type and picking_type.sequence_id:
            return picking_type.sequence_id.next_by_id()
        return False

    def action_auto_replenish(self):
        for record in self:
            record.write({'state': 'replenished'})

        self.ensure_one()
        self.product_line_ids.unlink()

        if self.replenishment_method == 'standard template' and self.standard_template:

            # Clear existing product lines
            # self.product_line_ids.unlink()

            # Group product lines by product_id and uom_id, summing the quantities
            grouped_lines = {}
            for product_line in self.standard_template.product_ids:
                key = (product_line.product_id.id, product_line.uom_id.id)
                if key not in grouped_lines:
                    grouped_lines[key] = {
                        'product_id': product_line.product_id,
                        'uom_id': product_line.uom_id,
                        'quantity': 0
                    }
                grouped_lines[key]['quantity'] += product_line.quantity

            # Create new product lines based on the grouped lines
            for _, line_data in grouped_lines.items():
                self.env['product.lines'].create({
                    'rep_request_id': self.id,  # Link to the current sfa.rep.request
                    'product_id': line_data['product_id'].id,
                    'product_uom_qty': line_data['quantity'],
                    'product_uom': line_data['uom_id'].id,
                    'date': fields.Datetime.now(),  # Set a default date
                })

        elif self.replenishment_method == 'salesman target' and self.target_name:
            # Clear existing moves
            # self.product_line_ids.unlink()

            # Group product lines by product_id, summing the targets
            grouped_lines = {}
            for product_line in self.target_name.product_lines:
                key = (product_line.product_id.id, product_line.uom_id.id)
                # key = product_line.product_id.id
                if key not in grouped_lines:
                    grouped_lines[key] = {
                        'product_id': product_line.product_id,
                        'uom_id': product_line.uom_id,
                        'target': 0
                    }
                grouped_lines[key]['target'] += product_line.target

                # Create new moves based on the grouped lines
            for _, line_data in grouped_lines.items():
                self.env['product.lines'].create({
                    # 'name': line_data['product_id'].name,
                    'rep_request_id': self.id,  # Link to the current sfa.rep.request
                    'product_id': line_data['product_id'].id,
                    'product_uom_qty': line_data['target'],
                    'product_uom': line_data['uom_id'].id,
                    'date': fields.Datetime.now(),  # Set a default date
                })

        self.auto_replenish_done = True

        # Return an action to reload the view
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def action_cancel(self):
        for record in self:
            # Find the associated stock.picking record by name
            picking = self.env['stock.picking'].sudo().search([
                ('name', '=', record.name)
            ], limit=1)

            if picking:
                if picking.state == 'done':
                    raise UserError(
                        "Cannot cancel a replenishment request with a completed picking.")

                # Cancel the picking
                picking.action_cancel()

            # Cancel the replenishment request
            record.write({'state': 'cancelled'})

        return True

    def action_submit_and_create_picking(self):
        for record in self:
            if not record.name:
                record.name = record.temp_name or record._get_new_name(
                    record.picking_type_id.id)
        self.ensure_one()

        # Create a new stock.picking record
        picking = self.env['stock.picking'].create({
            # Assuming salesman is a res.users record
            'name': self.name,
            'salesman': self.salesman.id,
            'picking_type_id': self.picking_type_id.id,
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'scheduled_date': self.scheduled_date,
            'origin': self.origin,
        })

        # Create stock.move lines
        for line in self.product_line_ids:
            self.env['stock.move'].create({
                'name': line.product_id.name,
                # 'salesman': self.salesman.id,
                'picking_type_id': self.picking_type_id.id,
                'product_id': line.product_id.id,
                'product_uom_qty': line.product_uom_qty,
                'product_uom': line.product_uom.id,
                'picking_id': picking.id,
                'location_id': self.location_id.id,
                'location_dest_id': self.location_dest_id.id,
                'date': line.date or self.scheduled_date,
                'date_deadline': line.date_deadline,
                'description_picking': line.description,
            })

        # Update the state of the replenishment request
        self.write({
            'state': 'submitted',
            'is_submitted': True
        })

    @api.onchange('salesman')
    def _compute_replenishment_method(self):
        for record in self:
            if record.salesman and record.salesman.Default_Replenish_method:
                record.replenishment_method = record.salesman.Default_Replenish_method

    @api.onchange('salesman', 'replenishment_method')
    def _compute_standard_template(self):
        for record in self:
            if record.salesman and record.salesman.Default_Template:
                record.standard_template = record.salesman.Default_Template

    @api.onchange('salesman', 'replenishment_method')
    def _compute_target_name(self):
        for record in self:
            if record.salesman and record.salesman.Default_Target:
                record.target_name = record.salesman.Default_Target

    @api.onchange('salesman', 'replenishment_method')
    def _compute_route(self):
        for record in self:
            if record.salesman and record.salesman.Default_route:
                record.route = record.salesman.Default_route

    @api.onchange('replenishment_method')
    def _onchange_standard_template(self):
        if self.replenishment_method != 'standard template':
            self.standard_template = False

    @api.onchange('replenishment_method')
    def _onchange_target_name(self):
        if self.replenishment_method != 'salesman target':
            self.target_name = False

    @api.onchange('replenishment_method')
    def _onchange_route(self):
        if self.replenishment_method != 'customer consumption':
            self.route = False

    @api.depends('salesman')
    def _compute_picking_type_id(self):
        for record in self:
            if record.salesman and record.salesman.Replenish_Operation_Type:
                record.picking_type_id = record.salesman.Replenish_Operation_Type
            else:
                # Fallback to default behavior if needed
                record.picking_type_id = self.env['stock.picking.type'].search(
                    [], limit=1)

    @api.depends('salesman')
    def _compute_location_id(self):
        for record in self:
            if record.salesman and record.salesman.Replenish_Operation_Type and record.salesman.Replenish_Operation_Type.default_location_src_id:
                record.location_id = record.salesman.Replenish_Operation_Type.default_location_src_id
            else:
                record.location_id = False

    @api.depends('salesman')
    def _compute_location_dest_id(self):
        for record in self:
            if record.salesman and record.salesman.Replenish_Operation_Type and record.salesman.Replenish_Operation_Type.default_location_dest_id:
                record.location_dest_id = record.salesman.Replenish_Operation_Type.default_location_dest_id
            else:
                record.location_dest_id = False
            # else:
            #     # Fallback to default behavior if needed
            #     record.location_id = self.env['stock.picking.type'].search(
            #         [], limit=1)

    allowed_route_ids = fields.Many2many(
        'sfa.journey.assignment', compute='_compute_allowed_route_ids', store=False)

    @api.depends('salesman')
    def _compute_allowed_route_ids(self):
        for record in self:
            if record.salesman:
                record.allowed_route_ids = self.env['sfa.journey.assignment'].search([
                    ('salesman_id', '=', record.salesman.id),
                    ('state', '=', True)
                ])
            else:
                record.allowed_route_ids = False
