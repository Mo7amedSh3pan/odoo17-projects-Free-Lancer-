from odoo import models, fields, api


class Region(models.Model):
    _name = 'sfa.region'
    _description = 'Region'

    code = fields.Char(string='Region Code', required=True)
    name = fields.Char(string='Region Name', required=True)
    description = fields.Text(string='Description')


class Stat(models.Model):
    _name = 'sfa.stat'
    _description = 'Stat'

    code = fields.Char(string='Stat Code', required=True)
    name = fields.Char(string='Stat Name', required=True)
    region_id = fields.Many2one('sfa.region', string='Region', required=True)
    description = fields.Text(string='Description')


class City(models.Model):
    _name = 'sfa.city'
    _description = 'City'

    code = fields.Char(string='City Code', required=True)
    name = fields.Char(string='City Name', required=True)
    stat_id = fields.Many2one('sfa.stat', string='Stat', required=True)
    description = fields.Text(string='Description')


class Area(models.Model):
    _name = 'sfa.area'
    _description = 'Area'

    code = fields.Char(string='Area Code', required=True)
    name = fields.Char(string='Area Name', required=True)
    city_id = fields.Many2one('sfa.city', string='City', required=True)
    description = fields.Text(string='Description')


class Territory(models.Model):
    _name = 'sfa.territory'
    _description = 'Territory'

    code = fields.Char(string='Territory Code', required=True)
    name = fields.Char(string='Territory Name', required=True)
    region_id = fields.Many2one('sfa.region', string='Region', required=True)
    stat_id = fields.Many2one('sfa.stat', string='Stat', required=True)
    city_id = fields.Many2one('sfa.city', string='City', required=True)
    area_id = fields.Many2one('sfa.area', string='Area', required=True)
    description = fields.Text(string='Description')
