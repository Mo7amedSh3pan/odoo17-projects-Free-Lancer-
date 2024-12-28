from odoo import models, fields, api
from odoo.exceptions import UserError


class WeekDay(models.Model):
    _name = 'week.day'
    _description = 'Day of the Week'

    name = fields.Char(string='Day', required=True)


class CustomerType(models.Model):
    _name = 'customer.type'
    _description = 'customer type'

    name = fields.Char(required=True)
    company_id = fields.Many2one('res.company', string='Company',
                                 domain="[('id', 'in', allowed_company_ids)]")

    @api.model
    def _get_allowed_companies(self):
        return self.env.companies.ids

    @api.model
    def default_get(self, fields):
        res = super(CustomerType, self).default_get(fields)
        res['company_id'] = self.env.company.id
        return res


class CustomerCategory(models.Model):
    _name = 'customer.category'
    _description = 'customer category'

    name = fields.Char(required=True)
    category_id = fields.Integer(string='ID')
    company_id = fields.Many2one('res.company', string='Company',
                                 domain="[('id', 'in', allowed_company_ids)]")

    @api.model
    def _get_allowed_companies(self):
        return self.env.companies.ids

    @api.model
    def default_get(self, fields):
        res = super(CustomerCategory, self).default_get(fields)
        res['company_id'] = self.env.company.id
        return res


class ResPartner(models.Model):
    _inherit = 'res.partner'

    latitude = fields.Char(string='Latitude')
    longitude = fields.Char(string='Longitude')

    territory_id = fields.Many2one(
        'sfa.territory',
        string='Territory',
    )

    customer_type_id = fields.Many2one(
        'customer.type',
    )

    customer_category_id = fields.Many2one(
        'customer.category',
    )

    open_close_time_start = fields.Float(
        widget='float_time')
    open_close_time_start_ampm = fields.Selection(
        [('am', 'AM'), ('pm', 'PM')], string='Opening Time AM/PM')

    open_close_time_end = fields.Float(
        widget='float_time')
    open_close_time_end_ampm = fields.Selection(
        [('am', 'AM'), ('pm', 'PM')], string='Closing Time AM/PM')

    visit_time_preference_from = fields.Float(
        string='From', widget='float_time')
    visit_time_preference_from_ampm = fields.Selection(
        [('am', 'AM'), ('pm', 'PM')], string='Visit Time From AM/PM')

    visit_time_preference_to = fields.Float(
        string='To', widget='float_time')
    visit_time_preference_to_ampm = fields.Selection(
        [('am', 'AM'), ('pm', 'PM')], string='Visit Time To AM/PM')

    working_days = fields.Many2many(
        'week.day',
        string='Working Days',
    )

    def action_show_map(self):
        self.ensure_one()
        if not self.latitude or not self.longitude:
            if self.env.user.lang == 'en_US':
                raise UserError(
                    "Both latitude and longitude must be provided to show the map.")
            elif self.env.user.lang == 'ar_001':
                raise UserError(
                    "يجب توفير كل من خط الطول وخط العرض لإظهار الخريطة.")

        return {
            'type': 'ir.actions.act_url',
            'url': f'https://www.google.com/maps/search/?api=1&query={self.latitude},{self.longitude}',
            'target': 'new'
        }
