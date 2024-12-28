from odoo import models, fields, api
from odoo.osv import expression


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    computed_domain = fields.Many2many('res.users', compute="_compute_user_domain")

    @api.depends('invoice_user_id')
    def _compute_user_domain(self):
        for record in self:
            record.computed_domain = self.env['res.users'].search(self._get_user_domain())

    @api.model
    def _get_user_domain(self):
        # Your custom domain logic
        if self.env.user.sales_manager:
            return []

        teams = self.env['crm.team'].search([('user_id', '=', self.env.uid)])
        if not teams:
            return [('id', '=', self.env.uid)]

        team_member_user_ids = self.env['crm.team.member'].search([
            ('crm_team_id', 'in', teams.ids)
        ]).mapped('user_id').ids
        team_member_user_ids.append(self.env.uid)
        return [('id', 'in', team_member_user_ids)]

    invoice_user_id = fields.Many2one(
        'res.users',
        string='Salesperson',
        domain=lambda self: self._get_user_domain(),
    )

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
        """
        Override _search to implement custom access control:
        - Sales managers can see all records
        - Team leaders can only see records where invoice_user_id is a member of their teams
        - Only apply to invoices and credit notes (move_type in ['out_invoice', 'out_refund'])
        """
        user = self.env.user

        # If user is sales manager, no restrictions
        if user.sales_manager:
            return super()._search(domain, offset=offset, limit=limit, order=order,
                                   access_rights_uid=access_rights_uid)

        # Find all teams where current user is leader
        teams = self.env['crm.team'].search([
            ('user_id', '=', user.id)
        ])

        if teams:
            # Get all users who are members of these teams
            team_member_user_ids = self.env['crm.team.member'].search([
                ('crm_team_id', 'in', teams.ids)
            ]).mapped('user_id').ids

            # Create domain to filter by team member user_ids only
            # Also restrict to customer invoices and credit notes
            user_domain = [
                ('invoice_user_id', 'in', list(set(team_member_user_ids + ([self.env.uid])))),
                ('move_type', 'in', ['out_invoice', 'out_refund'])
            ]

        else:
            # If user is not a team leader and not a sales manager,
            # they should not see any records
            domain = expression.AND([domain or [], [('invoice_user_id', '=', self.env.uid)]])

        return super()._search(domain, offset=offset, limit=limit, order=order,
                               access_rights_uid=access_rights_uid)
