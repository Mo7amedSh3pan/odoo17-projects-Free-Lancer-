from odoo import models, fields, api
from odoo.osv import expression


class PosSessionInherit(models.Model):
    _inherit = 'pos.session'


    user_id = fields.Many2one(
        'res.users',
        string='Opened By',
    )

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
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
                ('user_id', 'in', list(set(team_member_user_ids + ([self.env.uid]))))
            ]

        else:
            # If user is not a team leader and not a sales manager,
            # they should not see any records
            domain = expression.AND([domain or [], [('user_id', '=', self.env.uid)]])

        return super()._search(domain, offset=offset, limit=limit, order=order,
                               access_rights_uid=access_rights_uid)

class PosOrderInherit(models.Model):
    _inherit = 'pos.order'

    employee_id = fields.Many2one(
        'hr.employee',
    )

    @api.model
    def _search(self, args, offset=0, limit=None, order=None):
        # If user is sales manager, return all records without additional filtering
        if self.env.user.sales_manager:
            return super()._search(args, offset=offset, limit=limit, order=order)

        # Get current user's employee record
        current_employee = self.env['hr.employee'].search([
            ('user_id', '=', self.env.uid)
        ], limit=1)

        # Find teams where current user is leader
        teams = self.env['crm.team'].search([
            ('user_id', '=', self.env.uid)
        ])

        if teams:
            # Get all team members' employee IDs
            team_member_ids = self.env['crm.team.member'].search([
                ('crm_team_id', 'in', teams.ids)
            ]).mapped('user_id.employee_id').ids

            # Add domain to filter by salesman_id
            domain = [('employee_id', 'in', list(set(team_member_ids + ([current_employee.id] if current_employee else []))))]
            args = expression.AND([args or [], domain])

        elif current_employee:  # If no teams but employee exists, only show their records
            domain = [('employee_id', 'in', [current_employee.id])]
            args = expression.AND([args or [], domain])
        elif not current_employee:  # If no teams but employee exists, only show their records
            domain = [('employee_id', 'in', [])]
            args = expression.AND([args or [], domain])
        return super()._search(args, offset=offset, limit=limit, order=order)
