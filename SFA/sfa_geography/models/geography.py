from odoo import models, fields, api


class Region(models.Model):
    _name = 'sfa.region'
    _description = 'Region'

    code = fields.Char(string='Region Code', required=True)
    name = fields.Char(string='Region Name', required=True)
    description = fields.Text(string='Description')


class Stat(models.Model):
    _name = 'sfa.stat'
    _description = 'state'

    code = fields.Char(string='state Code', required=True)
    name = fields.Char(string='state Name', required=True)
    region_id = fields.Many2one('sfa.region', string='Region')
    description = fields.Text(string='Description')


class City(models.Model):
    _name = 'sfa.city'
    _description = 'City'

    code = fields.Char(string='City Code', required=True)
    name = fields.Char(string='City Name', required=True)
    stat_id = fields.Many2one('sfa.stat', string='Stat')
    description = fields.Text(string='Description')


class Area(models.Model):
    _name = 'sfa.area'
    _description = 'Area'

    code = fields.Char(string='Area Code', required=True)
    name = fields.Char(string='Area Name', required=True)
    city_id = fields.Many2one('sfa.city', string='City')
    description = fields.Text(string='Description')


class Territory(models.Model):
    _name = 'sfa.territory'
    _description = 'Territory'

    code = fields.Char(string='Territory Code', required=True)
    name = fields.Char(string='Territory Name', required=True)
    region_id = fields.Many2one('sfa.region', string='Region')

    stat_id = fields.Many2one(
        'sfa.stat',
        string='Stat',
        domain="[('region_id', '=', region_id)]"
    )
    city_id = fields.Many2one(
        'sfa.city',
        string='City',
        domain="[('stat_id', '=', stat_id)]"
    )

    area_id = fields.Many2one(
        'sfa.area',
        string='Area',
        domain="[('city_id', '=', city_id)]"
    )

    description = fields.Text(string='Description')
    company_id = fields.Many2one('res.company', string='Company',
                                 domain="[('id', 'in', allowed_company_ids)]")
    status = fields.Selection([
        ('enable', 'Enable'),
        ('disable', 'Disable')
    ], string='status', default='enable')

    @api.model
    def _get_allowed_companies(self):
        return self.env.companies.ids

    @api.model
    def default_get(self, fields):
        res = super(Territory, self).default_get(fields)
        res['company_id'] = self.env.company.id
        return res
