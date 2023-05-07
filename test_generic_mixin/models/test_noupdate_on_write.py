from odoo import models, fields


class TestNoUpdateOnWrite(models.Model):
    _name = 'test.generic.mixin.noupdate.on.write.model'
    _inherit = [
        'generic.mixin.data.updatable',
    ]
    _description = "Test Generic Mixin: No Update On Write Model"
    _auto_set_noupdate_on_write = True

    name = fields.Char()
