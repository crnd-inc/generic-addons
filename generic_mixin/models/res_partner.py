from odoo import models, fields


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'generic.mixin.refresh.view']
