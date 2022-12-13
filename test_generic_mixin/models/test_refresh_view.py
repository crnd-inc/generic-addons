from odoo import models, fields


class TestGMRefreshView(models.Model):
    _name = 'test.gm.refresh.view'
    _inherit = 'generic.mixin.refresh.view'

    name = fields.Char(translate=True)
    description = fields.Text()
