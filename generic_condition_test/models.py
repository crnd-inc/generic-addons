# -*- coding: utf-8 -*-
from openerp import models, fields


class TestConditionDateDiff(models.Model):
    _name = 'test.generic.condition.date.diff'

    date_start = fields.Datetime()
    date_end = fields.Datetime()

    date_test = fields.Date()
