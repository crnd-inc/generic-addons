# -*- coding: utf-8 -*-
from openerp import models, fields, api


class RequestType(models.Model):
    _inherit = "request.type"

    # Request type has no websitepublish url yet, so we just need
    # website_published field, thus implement it in explicit way here insetead
    # of inheriting from "website.published.mixin"
    website_published = fields.Boolean('Visible in Website', copy=False)

    @api.multi
    def website_publish_button(self):
        self.write({'website_published': True})
        return True
