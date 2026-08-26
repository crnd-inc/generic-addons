from odoo import models, fields

# Fixtures for read_counts_for / read_counts_for_o2m.


class TestX2mAggParent(models.Model):
    _name = 'test.generic.mixin.x2m.agg.parent'
    _description = "Test Generic Mixin: x2m agg: Parent"
    _order = 'name'

    name = fields.Char()
    code = fields.Char()
    child_ids = fields.One2many(
        'test.generic.mixin.x2m.agg.child', 'parent_id')
    # Explicit relation: the generated name exceeds PostgreSQL's 63 chars.
    other_ids = fields.Many2many(
        'test.generic.mixin.x2m.agg.child',
        relation='test_gm_x2m_agg_other_rel',
        column1='parent_id', column2='child_id')


class TestX2mAggChild(models.Model):
    _name = 'test.generic.mixin.x2m.agg.child'
    _description = "Test Generic Mixin: x2m agg: Child"
    _order = 'name'

    name = fields.Char()
    active = fields.Boolean(default=True)
    parent_id = fields.Many2one('test.generic.mixin.x2m.agg.parent')
    parent_code = fields.Char()
