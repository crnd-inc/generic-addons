import logging
from odoo import fields, models, api, _
from odoo.tools import single_email_re
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class GenericMixinContact(models.AbstractModel):
    _name = 'generic.mixin.contact'
    _description = 'Generic Mixin: Contacts'

    # Contacts block
    phone = fields.Char()
    email = fields.Char()

    website_link = fields.Char()
    link_fb = fields.Char()
    link_linkedin = fields.Char()
    link_viber = fields.Char()
    link_telegram = fields.Char()
    link_youtube = fields.Char()
    link_twitter = fields.Char()
    link_whatsapp = fields.Char()

    # Address block
    location_street = fields.Char()
    location_street2 = fields.Char()
    location_city = fields.Char()
    location_zip = fields.Char()
    location_state_id = fields.Many2one('res.country.state')
    location_country_id = fields.Many2one('res.country')

    # Email validation
    @api.constrains('email')
    def _check_email(self):
        if self.email and not single_email_re.match(self.email):
            raise UserError(
                _("Invalid Email! Please enter a valid email address."))

    # Website link sanitizer
    def write(self, vals):
        if vals.get('website_link'):
            vals['website_link'] = self.env['res.partner']._clean_website(
                vals['website_link'])
        return super(GenericMixinContact, self).write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('website_link'):
                vals['website_link'] = self.env['res.partner']._clean_website(
                    vals['website_link'])
        return super(GenericMixinContact, self).create(vals_list)
