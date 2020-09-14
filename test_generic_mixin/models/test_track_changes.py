from odoo import models, fields
from odoo.addons.generic_mixin import pre_write, post_write


class TestTrackChangesModel(models.Model):
    _name = 'test.generic.mixin.track.changes.model'
    _inherit = [
        'generic.mixin.track.changes',
        'generic.mixin.data.updatable',
    ]

    name = fields.Char()
    value1 = fields.Integer()
    value2 = fields.Integer()
    value3 = fields.Integer()
    value4 = fields.Integer()
    description = fields.Text()

    @pre_write('value1', 'value2')
    def _pre_write_values_12(self, changes):
        res = ""
        if 'value1' in changes:
            res += "v1: %s -> %s\n" % changes['value1']
        if 'value2' in changes:
            res += "v2: %s -> %s\n" % changes['value2']

        return {'description': res}

    @post_write('value3', 'value4')
    def _post_write_values_34(self, changes):
        res = ""
        if 'value3' in changes:
            res += "v3: %s -> %s\n" % changes['value3']
        if 'value4' in changes:
            res += "v4: %s -> %s\n" % changes['value4']

        self.description = res
