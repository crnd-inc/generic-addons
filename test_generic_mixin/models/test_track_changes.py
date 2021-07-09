# pylint: disable=consider-merging-classes-inherited
from odoo import models, fields
from odoo.addons.generic_mixin import (
    pre_write,
    post_write,
    pre_create,
    post_create,
)


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
    value5 = fields.Integer()
    value6 = fields.Integer()
    value7 = fields.Integer()
    value8 = fields.Integer()
    description = fields.Text()
    create_dbg = fields.Char()
    create_dbg2 = fields.Char()
    create_dbg3 = fields.Char()
    create_dbg4 = fields.Char()

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

    @post_write('value5')
    def _post_write_values_5_override(self, changes):
        self.description = "Test V5 change"

    @pre_write('value6')
    def _pre_write_priority_6_none(self, changes):
        return {'description': 'Priority 6-None'}

    @pre_write('value6', priority=15)
    def _pre_write_priority_6_15(self, changes):
        return {'description': 'Priority 6-15'}

    @pre_write('value7', priority=15)
    def _pre_write_priority_7_15(self, changes):
        return {'description': 'Priority 7-15'}

    @pre_write('value8', priority=5)
    def _pre_write_priority_8_5(self, changes):
        return {'description': 'Priority 8-5'}

    @pre_create()
    def _pre_create_set_dbg(self, changes):
        return {'create_dbg': 'pre-create-1'}

    @post_create()
    def _post_create_set_dbg(self, changes):
        self.create_dbg2 = 'post-create-1'

    @pre_create()
    def _precreate_set_dbg_3(self, changes):
        return {'create_dbg3': 'pre-create-3'}

    @post_create()
    def _post_create_set_dbg_4(self, changes):
        self.create_dbg4 = 'post-create-4'


class TestTrackChangesModelS1(models.Model):
    _inherit = 'test.generic.mixin.track.changes.model'

    value11 = fields.Integer()

    @post_write('value11')
    def _post_write_values_5_override(self, changes):
        res = super(
            TestTrackChangesModelS1, self
        )._post_write_values_5_override(changes)
        self.description = self.description + " Overriden"
        return res

    @pre_write('value7', priority=5)
    def _pre_write_priority_7_5(self, changes):
        return {'description': 'Priority 7-5'}

    # same method name as in base class, but without priority.
    # but still system have to pick first non-None priority specified on method
    @pre_write()
    def _pre_write_priority_8_5(self, changes):
        res = super(TestTrackChangesModelS1, self)._pre_write_priority_8_5(
            changes)
        res['description'] += '-x'
        return res

    @pre_write('value11')
    def _pre_create_set_dbg(self, changes):
        return super()._pre_create_set_dbg(changes)


class TestTrackChangesModelS2(models.Model):
    _inherit = 'test.generic.mixin.track.changes.model'

    value21 = fields.Integer()

    @post_write('value21')
    def _post_write_values_5_override(self, changes):
        return super(
            TestTrackChangesModelS2, self
        )._post_write_values_5_override(changes)

    @pre_write('value8')
    def _pre_write_priority_8_None(self, changes):
        return {'description': 'Priority 8-None'}

    @post_write('value21')
    def _post_create_set_dbg(self, changes):
        return super()._post_create_set_dbg(changes)
