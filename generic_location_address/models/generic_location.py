from odoo import models, fields, api


import logging
_logger = logging.getLogger(__name__)


def l_parent_get_field_names(field_name):
    hidden_field = '_%s' % field_name
    check_field = '%s_use_parent' % field_name
    return hidden_field, check_field


def l_parent_get_value(record, field_name):
    hfield, cfield = l_parent_get_field_names(field_name)

    if record[cfield] and record['parent_id']:
        return l_parent_get_value(record.parent_id, field_name)
    return record[hfield]


def l_parent_compute(field_name):
    hfield, cfield = l_parent_get_field_names(field_name)

    @api.depends(hfield, cfield, 'parent_id')
    def _compute_func(self):
        for record in self:
            record[field_name] = l_parent_get_value(
                record.sudo(), field_name)
    return _compute_func


def l_parent_inverse(field_name):
    hfield, cfield = l_parent_get_field_names(field_name)

    def _inverse_func(self):
        for record in self:
            if not record[cfield]:
                record[hfield] = record[field_name]
    return _inverse_func


class GenericLocation(models.Model):
    _inherit = 'generic.location'

    def _default_country_id(self):
        company = self.env.user.company_id
        return company.country_id

    street = fields.Char(
        compute=l_parent_compute('street'),
        inverse=l_parent_inverse('street'),
        store=False,
    )
    _street = fields.Char()
    street_use_parent = fields.Boolean(
        string="Use Parent Street"
    )

    street2 = fields.Char(
        compute=l_parent_compute('street2'),
        inverse=l_parent_inverse('street2'),
        store=False,
    )
    _street2 = fields.Char()
    street2_use_parent = fields.Boolean(
        string="Use Parent Street2"
    )

    zip = fields.Char(
        compute=l_parent_compute('zip'),
        inverse=l_parent_inverse('zip'),
        store=False,
    )
    _zip = fields.Char()
    zip_use_parent = fields.Boolean(
        string="Use Parent Zip"
    )

    city = fields.Char(
        compute=l_parent_compute('city'),
        inverse=l_parent_inverse('city'),
        store=False,
    )
    _city = fields.Char()
    city_use_parent = fields.Boolean(
        string="Use Parent City"
    )

    state_id = fields.Many2one(
        'res.country.state', string='State',
        compute=l_parent_compute('state_id'),
        inverse=l_parent_inverse('state_id'),
        store=False,
    )
    _state_id = fields.Many2one('res.country.state', string='State')
    state_id_use_parent = fields.Boolean(
        string="Use Parent State"
    )

    country_id = fields.Many2one(
        'res.country', string='Country',
        default=_default_country_id,
        compute=l_parent_compute('country_id'),
        inverse=l_parent_inverse('country_id'),
        store=False,
    )
    _country_id = fields.Many2one(
        'res.country', string='Country')
    country_id_use_parent = fields.Boolean(
        string="Use Parent Country"
    )

    @api.onchange('parent_id')
    def onchange_parent(self):
        for record in self:
            if record.parent_id:
                record.street_use_parent = True
                record.street2_use_parent = True
                record.zip_use_parent = True
                record.city_use_parent = True
                record.state_id_use_parent = True
                record.country_id_use_parent = True
            else:
                record.street_use_parent = False
                record.street2_use_parent = False
                record.zip_use_parent = False
                record.city_use_parent = False
                record.state_id_use_parent = False
                record.country_id_use_parent = False
