# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.tools import ustr
from openerp.exceptions import ValidationError

import logging
logger = logging.getLogger(__name__)


class TestGenericCondition(models.TransientModel):
    _name = 'generic.condition.test_condition'
    _description = "Wizard: Test generic condition"

    condition_id = fields.Many2one(
        'generic.condition', 'Condition', required=True, ondelete='cascade')
    res_model = fields.Char(
        string='Object Model',
        related='condition_id.model_id.model',
        readonly=True)
    res_id = fields.Integer(
        'Object ID', help='ID of object to test condition on')
    result = fields.Text(readonly=True)

    @api.multi
    def process(self):
        result_map = {
            True: _('Ok'),
            False: _('Fail'),
            None: _('Unknown'),
        }

        for wiz in self:
            TestModel = self.env[wiz.condition_id.model_id.model]

            if not TestModel.search([('id', '=', wiz.res_id)]):
                raise ValidationError(
                    _('Object (model: %s; id: %s) not found'
                      '') % (wiz.condition_id.model_id.model, wiz.res_id))
            else:
                test_obj = TestModel.browse(wiz.res_id)
                result = wiz.condition_id.check(test_obj)
                result = result_map.get(result, result)

                wiz.write({'result': ustr(result)})

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'generic.condition.test_condition',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': wiz.id,
                'views': [(False, 'form')],
                'target': 'new',
            }

        return {
            'type': 'ir.actions.act_window_close',
        }
