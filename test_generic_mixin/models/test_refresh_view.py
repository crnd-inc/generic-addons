from odoo import models, fields


class TestGMRefreshView(models.Model):
    _name = 'test.gm.refresh.view'
    _description = "Test Generic Mixin: Refresh View model"
    _inherit = 'generic.mixin.refresh.view'

    name = fields.Char(translate=True)
    description = fields.Text()
