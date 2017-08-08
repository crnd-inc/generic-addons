# -*- coding: utf-8 -*-
from openerp import models, fields, api


class RequestCategory(models.Model):
    _inherit = "request.category"

    # Request category has no websitepublish url yet, so we just need
    # website_published field, thus implement it in explicit way here insetead
    # of inheriting from "website.published.mixin"
    website_published = fields.Boolean(
        'Visible in Website', copy=False)
        # help='If set to True all child categories '
             # 'also will be visible on website'))

    @api.multi
    def website_publish_button(self):
        self.write({'website_published': True})
        return True

