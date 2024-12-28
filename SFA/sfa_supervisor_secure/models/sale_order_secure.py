from odoo import models, fields, api
from odoo.osv import expression


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _get_user_domain(self):
        # If user is sales manager, no restrictions
        if self.env.user.sales_manager:
            return []

        teams = self.env['crm.team'].search([
            ('user_id', '=', self.env.uid)
        ])

        if not teams:
            return [('id', '=', self.env.uid)]

        team_member_user_ids = self.env['crm.team.member'].search([
            ('crm_team_id', 'in', teams.ids)
        ]).mapped('user_id').ids

        # Add current employee's ID to the list
        team_member_user_ids.append(self.env.uid)

        return [('id', 'in', team_member_user_ids)]

    user_id = fields.Many2one(
        'res.users',
        string='Salesperson',
        domain=lambda self: self._get_user_domain(),
        default=lambda self: self.env.user
    )

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
        user = self.env.user

        if user.sales_manager:
            return super()._search(domain, offset=offset, limit=limit, order=order,
                                   access_rights_uid=access_rights_uid)

        teams = self.env['crm.team'].search([
            ('user_id', '=', user.id)
        ])

        if teams:
            team_member_user_ids = self.env['crm.team.member'].search([
                ('crm_team_id', 'in', teams.ids)
            ]).mapped('user_id').ids

            user_domain = [('user_id', 'in', list(set(team_member_user_ids + ([self.env.uid]))))]

            domain = expression.AND([domain or [], user_domain])
        else:
            domain = expression.AND([domain or [], [('user_id', '=', self.env.uid)]])

        return super()._search(domain, offset=offset, limit=limit, order=order,
                               access_rights_uid=access_rights_uid)

