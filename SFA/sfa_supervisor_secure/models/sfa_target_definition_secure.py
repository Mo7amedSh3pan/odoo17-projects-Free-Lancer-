# models/rep_request.py
from odoo import models, fields, api
from odoo.osv import expression


class TargetDefinitionInherit(models.Model):
    _inherit = 'sfa.target.definition'


    @api.model
    def _get_salesman_domain(self):

        if self.env.user.sales_manager:
            return []

        # Get the current user's employee record
        current_employee = self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1)

        if not current_employee:
            return [('id', 'in', [])]  # Returns empty list - no records will be shown

        # Find all teams where current user is leader
        teams = self.env['crm.team'].search([
            ('user_id', '=', self.env.uid)
        ])

        if not teams:
            return [('id', '=', current_employee.id)]

        # Get all employees who are members of these teams
        team_member_ids = self.env['crm.team.member'].search([
            ('crm_team_id', 'in', teams.ids)
        ]).mapped('user_id.employee_id').ids

        # Add current employee's ID to the list
        team_member_ids.append(current_employee.id)

        return [('id', 'in', team_member_ids)]

    salesman_id = fields.Many2one(
        'hr.employee',
        string="Salesman",
        domain=lambda self: self._get_salesman_domain()
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
            domain = [
                ('salesman_id', 'in', list(set(team_member_ids + ([current_employee.id] if current_employee else []))))]
            args = expression.AND([args or [], domain])

        elif current_employee:  # If no teams but employee exists, only show their records
            domain = [('salesman_id', 'in', [current_employee.id])]
            args = expression.AND([args or [], domain])
        elif not current_employee:  # If no teams but employee exists, only show their records
            domain = [('salesman_id', 'in', [])]
            args = expression.AND([args or [], domain])

        return super()._search(args, offset=offset, limit=limit, order=order)
