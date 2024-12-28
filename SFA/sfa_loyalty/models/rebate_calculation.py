# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
import ast
from ast import literal_eval
from dateutil.relativedelta import relativedelta

from odoo.fields import Float


class RebateCalculationLines(models.Model):
    _name = 'rebate.calculation.lines'
    _description = 'Rebate Calculation.lines'

    rebate_calculation_id = fields.Many2one('sfa.rebate.calculation')
    customer = fields.Many2one('res.partner')
    calculated_points = fields.Float(readonly=True)
    calculated_value = fields.Float(readonly=True)
    accrual_value = fields.Float()
    approved_value = fields.Float()
    reason = fields.Text()
    comment = fields.Text()

    @api.onchange('calculated_value', 'approved_value')
    def _onchange_accrual_value(self):
        for record in self:
            record.accrual_value = record.calculated_value - (record.approved_value or 0)


class AccountMove(models.Model):
    _inherit = 'account.move'

    rebate_calculation_id = fields.Many2one('sfa.rebate.calculation', string='Rebate Calculation', readonly=True)


class SFARebateCalculation(models.Model):
    _name = 'sfa.rebate.calculation'
    _description = 'SFA Rebate Calculation'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', required=True,
                       copy=False, readonly=True, default=lambda self: _('New'))
    rebate_calculation_line_ids = fields.One2many('rebate.calculation.lines', 'rebate_calculation_id')
    rebate_promotion = fields.Many2one('sfa.loyalty', required=True,domain="[('company_id', '=', branch_id)]")
    calc_name = fields.Char()
    credit_date = fields.Date()
    from_date = fields.Date()
    to_date = fields.Date()
    total_calculated_value = fields.Float(compute='_compute_totals', readonly=True, store=True)
    total_approved = fields.Float(compute='_compute_totals', store=True)
    total_accrual = fields.Float(compute='_compute_totals', store=True)
    total_points = fields.Float(compute='_compute_totals', store=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    branch_id = fields.Many2one(
        'res.company', string='Branch', default=lambda self: self.env.company,
        domain="[('id', 'in', allowed_company_ids)]")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('calculated', 'Calculated'),
        ('approved', 'Approved'),
        ('submitted', 'Submitted'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    is_approved = fields.Boolean(default=False)
    is_submitted = fields.Boolean(default=False)
    is_cancelled = fields.Boolean(default=False)

    # Add the credit_journal field
    # credit_journal = fields.Many2one('account.journal',
    #     string='Credit Note Journal',
    #     domain="[('type', '=', 'sale'), '|', ('company_id', '=', branch_id or company_id), ('company_id', '=', False)]",
    #     )
    # is_approved = fields.Boolean(default=False)

    @api.constrains('from_date', 'to_date')
    def _check_dates(self):
        for record in self:
            if record.from_date and record.to_date and record.from_date > record.to_date:
                raise ValidationError(_("From Date must be less than To Date"))

    @api.depends('rebate_calculation_line_ids.calculated_points', 'rebate_calculation_line_ids.calculated_value',
                 'rebate_calculation_line_ids.approved_value', 'rebate_calculation_line_ids.accrual_value')
    def _compute_totals(self):
        for record in self:
            record.total_points = sum(record.rebate_calculation_line_ids.mapped('calculated_points'))
            record.total_calculated_value = sum(record.rebate_calculation_line_ids.mapped('calculated_value'))
            record.total_approved = sum(record.rebate_calculation_line_ids.mapped('approved_value'))
            record.total_accrual = sum(record.rebate_calculation_line_ids.mapped('accrual_value'))

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq = self.env['ir.sequence'].next_by_code('sfa.rebate.calculation')
            if not seq:
                raise UserError(
                    _('Please define a sequence for the Request Set'))
            vals['name'] = seq
        return super(SFARebateCalculation, self).create(vals)

    def write(self, vals):
        if 'name' in vals and vals['name'] == _('New'):
            seq = self.env['ir.sequence'].next_by_code('sfa.rebate.calculation')
            if not seq:
                raise UserError(
                    _('Please define a sequence for the Request Set'))
            vals['name'] = seq
        return super(SFARebateCalculation, self).write(vals)

    def unlink(self, *args, **kwargs):
        for record in self:
            if record.state == 'approved':
                raise ValidationError(_("This record is approved and cannot be deleted."))
        return super(SFARebateCalculation, self).unlink(*args, **kwargs)

    # def action_submit_credit(self):
    #     self.state = 'submitted'
    #     self.is_submitted = True
    #     """Create credit notes from rebate calculation lines."""
    #     move_obj = self.env['account.move']
    #
    #     for record in self:
    #         # Find the appropriate sales journal
    #         # journal = self.env['account.journal'].search([
    #         #     ('type', '=', 'sale'),
    #         #     ('company_id', '=', record.company_id.id)
    #         # ], limit=1)
    #         #
    #         # if not journal:
    #         #     raise UserError(_('Please configure a sales journal for the company.'))
    #         # Group lines by customer to create one credit note per customer
    #         customer_lines = {}
    #         for line in record.rebate_calculation_line_ids:
    #             if line.customer not in customer_lines:
    #                 customer_lines[line.customer] = []
    #             customer_lines[line.customer].append(line)
    #
    #         # Create credit note for each customer
    #         for customer, lines in customer_lines.items():
    #             if not customer:
    #                 continue
    #
    #             if not self.rebate_promotion.reward_ids.credit_journal:
    #                 raise UserError(_('Credit journal is not configured in rebate promotion rewards'))
    #             credit_journal = self.rebate_promotion.reward_ids.credit_journal
    #             revenue_account = credit_journal.default_account_id
    #             print('#'*20)
    #             print('self.rebate_promotion.reward_ids.credit_journal')  # Add this for debugging
    #             print(self.rebate_promotion.reward_ids.credit_journal.id)  # Add this for debugging
    #             print('self.rebate_promotion.reward_ids.credit_journal.default_account_id')  # Add this for debugging
    #             print(self.rebate_promotion.reward_ids.credit_journal.default_account_id.id)  # Add this for debugging
    #             print('#'*20)
    #
    #             # Get payment terms from customer or default
    #             payment_term = customer.property_payment_term_id or self.env.ref(
    #                 'account.account_payment_term_immediate', raise_if_not_found=False)
    #
    #             invoice_date = record.credit_date or fields.Date.today()
    #             # Calculate due date based on payment terms or use invoice date
    #             # Simple due date calculation - using today's date as default
    #             due_date = invoice_date
    #             if payment_term and payment_term.line_ids:
    #                 first_term_line = payment_term.line_ids[0]
    #                 # Check which field exists for the payment term
    #                 if hasattr(first_term_line, 'delay'):
    #                     due_date = invoice_date + relativedelta(days=first_term_line.delay)
    #                 elif hasattr(first_term_line, 'day_of_the_month'):
    #                     # If using day of month payment terms
    #                     due_date = invoice_date + relativedelta(day=first_term_line.day_of_the_month)
    #
    #             move_vals = {
    #                 'move_type': 'out_refund',
    #                 'partner_id': customer.id,
    #                 'invoice_date': invoice_date,
    #                 'invoice_date_due': due_date,  # Add the due date
    #                 'invoice_payment_term_id': payment_term and payment_term.id or False,  # Add payment terms
    #                 'ref': f"Rebate Calculation - {self.name}",
    #                 'invoice_line_ids': [],
    #                 'company_id': self.branch_id.id,
    #                 'journal_id': credit_journal.id,
    #             }
    #
    #             if not revenue_account:
    #                 revenue_account = self.env['account.account'].search([
    #                     ('company_id', '=', self.branch_id.id),
    #                     ('account_type', '=', 'income'),  # or 'income_other' depending on your Odoo version
    #                     ('deprecated', '=', False)
    #                 ], limit=1)
    #
    #             if not revenue_account:
    #                 raise UserError(
    #                     _('Please configure a default account on the credit journal or set up a revenue account'))
    #
    #             # Add invoice lines for each rebate line
    #             for line in lines:
    #                 # Get the revenue account - you might want to configure this
    #
    #                 # revenue_account = self.env['account.account'].search([
    #                 #     ('company_id', '=', record.company_id.id),
    #                 #     # ('internal_type', '=', 'other'),
    #                 #     ('deprecated', '=', False)
    #                 # ], limit=1)
    #
    #                 # revenue_account = record.credit_journal.default_account_id
    #                 line_vals = {
    #                     'quantity': 1.0,
    #                     'price_unit': line.approved_value,
    #                     'account_id': revenue_account.id,
    #                     'product_id': self.rebate_promotion.reward_ids.discount_line_product_id.id,
    #                     'name': self.rebate_promotion.reward_ids.description,
    #                 }
    #
    #
    #
    #                 move_vals['invoice_line_ids'].append((0, 0, line_vals))
    #
    #             # Create the credit note
    #             if move_vals['invoice_line_ids']:
    #                 credit_note = move_obj.create(move_vals)
    #                 # You might want to add a reference back to the rebate calculation
    #                 # credit_note.write({'rebate_calculation_id': record.id})
    #
    #                 # Optional: Post the credit note automatically
    #                 # credit_note.action_post()
    #
    #     return True

    # Add new fields to store filtered lists

    @api.depends('branch_id')
    def _compute_default_journal(self):
        for record in self:
            journal = self.env['account.journal'].search([
                ('type', '=', 'sale'),
                ('company_id', '=', record.branch_id.id)
            ], limit=1)
            record.credit_journal = journal

    credit_journal = fields.Many2one('account.journal',
                                     string='Credit Note Journal',
                                     compute='_compute_default_journal',
                                     store=True,
                                     readonly=False,
                                     domain="[('type', '=', 'sale'), ('company_id', '=', branch_id)]"
                                     )

    def action_submit_credit(self):
        self.state = 'submitted'
        self.is_submitted = True
        """Create credit notes from rebate calculation lines."""
        move_obj = self.env['account.move']

        for record in self:
            # Group lines by customer to create one credit note per customer
            customer_lines = {}
            for line in record.rebate_calculation_line_ids:
                if line.customer not in customer_lines:
                    customer_lines[line.customer] = []
                customer_lines[line.customer].append(line)

            # Create credit note for each customer
            for customer, lines in customer_lines.items():
                if not customer:
                    continue

                if not self.rebate_promotion.reward_ids.credit_journal:
                    raise UserError(_('Credit journal is not configured in rebate promotion rewards'))
                credit_journal = self.rebate_promotion.reward_ids.credit_journal
                revenue_account = credit_journal.default_account_id
                print('#' * 20)
                print('self.rebate_promotion.reward_ids.credit_journal')  # Add this for debugging
                print(self.rebate_promotion.reward_ids.credit_journal.id)  # Add this for debugging
                print('self.rebate_promotion.reward_ids.credit_journal.default_account_id')  # Add this for debugging
                print(self.rebate_promotion.reward_ids.credit_journal.default_account_id.id)  # Add this for debugging
                print('#' * 20)

                # Get payment terms from customer or default
                payment_term = customer.property_payment_term_id or self.env.ref(
                    'account.account_payment_term_immediate', raise_if_not_found=False)

                invoice_date = record.credit_date or fields.Date.today()
                # Calculate due date based on payment terms or use invoice date
                # Simple due date calculation - using today's date as default
                due_date = invoice_date
                # if payment_term and payment_term.line_ids:
                #     first_term_line = payment_term.line_ids[0]
                #     # Check which field exists for the payment term
                #     if hasattr(first_term_line, 'delay'):
                #         due_date = invoice_date + relativedelta(days=first_term_line.delay)
                #     elif hasattr(first_term_line, 'day_of_the_month'):
                #         # If using day of month payment terms
                #         due_date = invoice_date + relativedelta(day=first_term_line.day_of_the_month)

                move_vals = {
                    'move_type': 'out_refund',
                    'partner_id': customer.id,
                    'invoice_date': invoice_date,
                    'invoice_date_due': due_date,  # Add the due date
                    # # 'invoice_payment_term_id': payment_term and payment_term.id or False,  # Add payment terms
                    'ref': f"Rebate Calculation - {self.name}",
                    'invoice_line_ids': [],
                    'company_id': self.branch_id.id,
                    'journal_id': credit_journal.id,
                }

                # if not revenue_account:
                #     revenue_account = self.env['account.account'].search([
                #         ('company_id', '=', self.branch_id.id),
                #         ('account_type', '=', 'income'),  # or 'income_other' depending on your Odoo version
                #         ('deprecated', '=', False)
                #     ], limit=1)

                # if not revenue_account:
                #     raise UserError(
                #         _('Please configure a default account on the credit journal or set up a revenue account'))

                # Add invoice lines for each rebate line
                for line in lines:
                    # Get the revenue account - you might want to configure this

                    # revenue_account = self.env['account.account'].search([
                    #     ('company_id', '=', record.company_id.id),
                    #     # ('internal_type', '=', 'other'),
                    #     ('deprecated', '=', False)
                    # ], limit=1)

                    # revenue_account = record.credit_journal.default_account_id
                    line_vals = {
                        'quantity': 1.0,
                        'price_unit': line.approved_value,
                        'account_id': self.rebate_promotion.reward_ids.credit_journal.default_account_id.id,
                        'product_id': self.rebate_promotion.reward_ids.discount_line_product_id.id,
                        'name': self.rebate_promotion.reward_ids.description,
                    }

                    move_vals['invoice_line_ids'].append((0, 0, line_vals))

                # Create the credit note
                # if move_vals['invoice_line_ids']:
                    credit_note = move_obj.create(move_vals)
                    # You might want to add a reference back to the rebate calculation
                    # credit_note.write({'rebate_calculation_id': record.id})

                    # Optional: Post the credit note automatically
                    # credit_note.action_post()

        return True



    # def action_submit_credit(self):
    #     """
    #     Create and submit credit notes from rebate calculation lines.
    #     Groups lines by customer and creates one credit note per customer.
    #     """
    #     self.ensure_one()
    #     move_obj = self.env['account.move']
    #
    #     if not self.branch_id:
    #         raise UserError(_('Please select a branch before creating credit notes.'))
    #
    #     # Update state
    #     self.write({
    #         'state': 'submitted',
    #         'is_submitted': True
    #     })
    #
    #     # Validate reward configuration
    #     if not self.rebate_promotion.reward_ids:
    #         raise UserError(_('No rewards configured for this rebate promotion.'))
    #
    #     reward = self.rebate_promotion.reward_ids
    #
    #     # Find appropriate journal for the branch
    #     credit_journal = self.env['account.journal'].search([
    #         ('type', '=', 'sale'),
    #         ('company_id', '=', self.branch_id.id)
    #     ], limit=1)
    #
    #     if not credit_journal:
    #         raise UserError(
    #             _('No sale journal found for branch %s. Please configure a sales journal.') % self.branch_id.name)
    #
    #     if not reward.discount_line_product_id:
    #         raise UserError(_('Discount product is not configured in rebate promotion rewards.'))
    #
    #     # Get company-specific revenue account
    #     # revenue_account = False
    #     product = reward.discount_line_product_id.with_company(self.branch_id)
    #
    #     # Check revenue account from product or category within the correct company
    #     # if product.property_account_income_id and product.property_account_income_id.company_id == self.branch_id:
    #     #     revenue_account = product.property_account_income_id
    #     # elif product.categ_id.property_account_income_categ_id and product.categ_id.property_account_income_categ_id.company_id == self.branch_id:
    #     #     revenue_account = product.categ_id.property_account_income_categ_id
    #     # elif credit_journal.default_account_id and credit_journal.default_account_id.company_id == self.branch_id:
    #     #     revenue_account = credit_journal.default_account_id
    #     # else:
    #     #     # Last resort: search for an income account in the correct company
    #     #     revenue_account = self.env['account.account'].search([
    #     #         ('company_id', '=', self.branch_id.id),
    #     #         ('account_type', '=', 'income'),
    #     #         ('deprecated', '=', False)
    #     #     ], limit=1)
    #
    #     # if not revenue_account:
    #     #     raise UserError(
    #     #         _('No appropriate revenue account found for branch %s. Please configure the product or journal with proper accounts.') % self.branch_id.name)
    #
    #     # Group lines by customer
    #     customer_lines = {}
    #     for line in self.rebate_calculation_line_ids:
    #         if not line.customer:
    #             continue
    #         customer_lines.setdefault(line.customer, []).append(line)
    #
    #     created_credit_notes = self.env['account.move']
    #     for customer, lines in customer_lines.items():
    #         # Get customer payment terms
    #         payment_term = customer.property_payment_term_id or self.env.ref(
    #             'account.account_payment_term_immediate', raise_if_not_found=False)
    #
    #         # Set dates
    #         invoice_date = self.credit_date or fields.Date.today()
    #
    #         # Calculate due date
    #         if payment_term and payment_term.line_ids:
    #             max_days = max(
    #                 (term.delay * {'days': 1, 'weeks': 7, 'months': 30, 'years': 365}[term.delay_type]
    #                  for term in payment_term.line_ids),
    #                 default=0
    #             )
    #             due_date = invoice_date + relativedelta(days=max_days)
    #         else:
    #             due_date = invoice_date
    #
    #         # Get company-specific taxes
    #         taxes = product.taxes_id.filtered(lambda t: t.company_id == self.branch_id)
    #
    #         # Ensure receivable account belongs to the correct company
    #         receivable_account = customer.property_account_receivable_id
    #         if not receivable_account or receivable_account.company_id != self.branch_id:
    #             raise UserError(
    #                 _('The receivable account for customer %s is associated with a different company.') % customer.name)
    #
    #         # Prepare credit note values
    #         move_vals = {
    #             'move_type': 'out_refund',
    #             'partner_id': customer.id,
    #             'invoice_date': invoice_date,
    #             'invoice_date_due': due_date,
    #             'payment_reference': f"Rebate Credit Note - {self.name}",
    #             'invoice_payment_term_id': payment_term.id if payment_term else False,
    #             'ref': f"Rebate Credit Note - {self.name}",
    #             'narration': f"Rebate Calculation Reference: {self.name}",
    #             'journal_id': credit_journal.id,
    #             'company_id': self.branch_id.id,
    #             'rebate_calculation_id': self.id,
    #             'invoice_origin': self.name,
    #             'invoice_line_ids': [
    #                 (0, 0, {
    #                     'name': f"{reward.description or 'Rebate Credit'} - {self.name}",
    #                     'quantity': 1.0,
    #                     'price_unit': line.approved_value,
    #                     'product_id': product.id,
    #                     # 'account_id': revenue_account.id,
    #                     'tax_ids': [(6, 0, taxes.ids)],
    #                     'date_maturity': due_date,
    #                 }) for line in lines
    #             ],
    #         }
    #
    #         # Create credit note in correct company context
    #         try:
    #             credit_note = move_obj.with_company(self.branch_id).create(move_vals)
    #             created_credit_notes |= credit_note
    #         except Exception as e:
    #             raise UserError(_('Error creating credit note for %s: %s') % (customer.name, str(e)))
    #
    #     if not created_credit_notes:
    #         raise UserError(_('No credit notes were created. Please check the configuration.'))
    #
    #     # Return action to view created credit notes
    #     action = {
    #         'name': _('Created Credit Notes'),
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'account.move',
    #         'view_mode': 'tree,form',
    #         'domain': [('id', 'in', created_credit_notes.ids)],
    #         'context': {'create': False}
    #     }
    #     return action
    #
    # def _calculate_due_date(self, invoice_date, payment_term):
    #     """Calculate due date based on payment terms."""
    #     if not payment_term or not payment_term.line_ids:
    #         return invoice_date
    #
    #     first_term_line = payment_term.line_ids[0]
    #     if hasattr(first_term_line, 'days'):
    #         return invoice_date + relativedelta(days=first_term_line.days)
    #     elif hasattr(first_term_line, 'day_of_the_month'):
    #         return invoice_date + relativedelta(day=first_term_line.day_of_the_month)
    #
    #     return invoice_date

    filtered_product_ids = fields.Many2many('product.product', string="Filtered Products")
    filtered_customer_ids = fields.Many2many('res.partner', string="Filtered Customers")

    def action_calculate(self):
        if not self.from_date or not self.to_date:
            raise ValidationError(_("From Date and To Date can't be empty"))
        else:
            self.ensure_one()
            self.rebate_calculation_line_ids.unlink()
            self.state = 'calculated'
            # print('from action_calculate method')
            for record in self:
                amount_rule = 0
                if record.rebate_promotion.rule_ids.qty_or_purchase == 'quantity':
                    amount_rule = record.rebate_promotion.rule_ids.minimum_qty
                elif record.rebate_promotion.rule_ids.qty_or_purchase == 'purchase':
                    amount_rule = record.rebate_promotion.rule_ids.minimum_amount
                reward_rule = record.rebate_promotion.rule_ids.reward_point_amount
                required_points_reward = record.rebate_promotion.reward_ids.required_points
                reward_reward = record.rebate_promotion.reward_ids.amount
                # Initialize domain lists
                product_domain = []
                customer_domain = []

                # Access loyalty program rules to get domains
                if record.rebate_promotion and record.rebate_promotion.rule_ids:
                    for rule in record.rebate_promotion.rule_ids:
                        # Append domain values
                        if rule.product_domain:
                            try:
                                product_domain.extend(eval(rule.product_domain))  # Evaluate to get actual domain list
                            except Exception as e:
                                _logger.error(f"Error evaluating product_domain for rule {rule.id}: {e}")
                        if rule.customer_domain:
                            try:
                                customer_domain.extend(eval(rule.customer_domain))  # Evaluate to get actual domain list
                            except Exception as e:
                                _logger.error(f"Error evaluating customer_domain for rule {rule.id}: {e}")

                # Use the evaluated domains to filter products and customers
                filtered_products = self.env['product.product'].search(product_domain if product_domain else [])
                filtered_customers = self.env['res.partner'].search(customer_domain if customer_domain else [])

                # Store filtered records in Many2many fields
                record.filtered_product_ids = [(6, 0, filtered_products.ids)]
                record.filtered_customer_ids = [(6, 0, filtered_customers.ids)]

                # Print product names using mapped to handle multiple records safely
                product_names = ", ".join(record.filtered_product_ids.mapped('name'))
                # print(f"Product names: {product_names}")

                # Dictionary to store totals per customer
                customer_totals = {}

                # Fetch invoices and filter based on filtered_customers
                invoice_records = self.env['account.move'].search(
                    [('move_type', '=', 'out_invoice'),
                     ('partner_id', 'in', filtered_customers.ids),
                     ('invoice_date', '>=', record.from_date),
                     ('invoice_date', '<=', record.to_date),
                     ('state', '=', 'posted')]
                )
                credit_note_records = self.env['account.move'].search(
                    [('move_type', '=', 'out_refund'),
                     ('partner_id', 'in', filtered_customers.ids),
                     ('invoice_date', '>=', record.from_date),
                     ('invoice_date', '<=', record.to_date),
                     ('state', '=', 'posted')]
                )

                # Iterate over each invoice
                for invoice in invoice_records:
                    total = 0
                    # Iterate over each line in account.move.line
                    for line in invoice.invoice_line_ids:
                        # Check if the line's product is in filtered_products by ID
                        # print('line.product_id.id')
                        # print(line.product_id.id)
                        # print('record.filtered_product_ids.ids')
                        # print(record.filtered_product_ids.ids)
                        # print('amount_rule')
                        # print(amount_rule)
                        # print('reward_rule')
                        # print(reward_rule)

                        if line.product_id.id in record.filtered_product_ids.ids:
                            if record.rebate_promotion.rule_ids.minimum_amount_tax_mode == 'incl':
                                total += line.price_total
                            elif record.rebate_promotion.rule_ids.minimum_amount_tax_mode == 'excl':
                                total += line.price_subtotal

                    # Add total to customer_totals
                    if invoice.partner_id not in customer_totals:
                        customer_totals[invoice.partner_id] = total
                        print('invoice.partner_id')
                        print(invoice.partner_id)
                        print('total')
                        print(total)
                    else:
                        customer_totals[invoice.partner_id] += total  # Iterate over each invoice
                        print('total')
                        print(total)

                for credit in credit_note_records:
                    total_credit = 0
                    # Iterate over each line in account.move.line
                    for line in credit.invoice_line_ids:

                        if line.product_id.id in record.filtered_product_ids.ids:
                            if record.rebate_promotion.rule_ids.minimum_amount_tax_mode == 'incl':
                                total_credit += line.price_total
                            elif record.rebate_promotion.rule_ids.minimum_amount_tax_mode == 'excl':
                                total_credit += line.price_subtotal

                    # Add total to customer_totals
                    if credit.partner_id not in customer_totals:
                        customer_totals[invoice.partner_id] -= total_credit
                        print('total_credit')
                        print(total_credit)
                    else:
                        customer_totals[invoice.partner_id] -= total_credit
                        print('total_credit')
                        print(total_credit)

                # Create rebate calculation lines with total for each customer
                for partner, total_value in customer_totals.items():
                    calculated_points = float((total_value / amount_rule) * reward_rule)
                    calculated_value = float((calculated_points / required_points_reward) * reward_reward)
                    self.env['rebate.calculation.lines'].create({
                        'rebate_calculation_id': record.id,
                        'customer': partner.id,
                        'calculated_points': calculated_points,
                        'calculated_value': calculated_value,
                        'approved_value': calculated_value,
                    })

                # Update total_calculated_value based on customer totals
                # record.total_points = sum(customer_totals.values())

    def action_approve(self):
        if not self.credit_date:
            raise ValidationError(_("Credit Date can't be empty"))
        else:
            self.is_approved = True
            self.state = 'approved'

    def action_cancel(self):
        self.state = 'cancelled'
        self.is_cancelled = True

