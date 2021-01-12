from odoo import models, fields

# Different type of usages of mixin


class TestNameBySequenceNoField(models.Model):
    _name = 'test.generic.mixin.name.by.sequence.nf'
    _inherit = [
        'generic.mixin.name.by.sequence',
    ]
    _name_by_sequence_auto_add_field = True
    _name_by_sequence_sequence_code = (
        'generic.mixin.test.name.by.sequence.name')


class TestNameBySequenceCustomField(models.Model):
    _name = 'test.generic.mixin.name.by.sequence.cf'
    _inherit = [
        'generic.mixin.name.by.sequence',
    ]
    _name_by_sequence_auto_add_field = True
    _name_by_sequence_name_field = 'my_name'
    _name_by_sequence_sequence_code = (
        'generic.mixin.test.name.by.sequence.name')


class TestNameBySequenceCustomFieldCustomName(models.Model):
    _name = 'test.generic.mixin.name.by.sequence.cfcn'
    _inherit = [
        'generic.mixin.name.by.sequence',
    ]
    _name_by_sequence_auto_add_field = True
    _name_by_sequence_name_field = 'my_name'
    _name_by_sequence_sequence_code = (
        'generic.mixin.test.name.by.sequence.name')

    my_name = fields.Char('My Name Field')


class TestNameBySequenceNoSequence(models.Model):
    _name = 'test.generic.mixin.name.by.sequence.ns'
    _inherit = [
        'generic.mixin.name.by.sequence',
    ]
    _name_by_sequence_auto_add_field = True


class TestNameBySequenceNoSequenceNoField(models.Model):
    _name = 'test.generic.mixin.name.by.sequence.nsnf'
    _inherit = [
        'generic.mixin.name.by.sequence',
    ]


class TestNameBySequenceNoFieldCustomField(models.Model):
    _name = 'test.generic.mixin.name.by.sequence.nfcf'
    _inherit = [
        'generic.mixin.name.by.sequence',
    ]
    _name_by_sequence_sequence_code = (
        'generic.mixin.test.name.by.sequence.name')

    name = fields.Char(default='New')


class TestNameBySequenceNoSequenceNoFieldCustomField(models.Model):
    _name = 'test.generic.mixin.name.by.sequence.nsnfcf'
    _inherit = [
        'generic.mixin.name.by.sequence',
    ]

    name = fields.Char(default='New')
