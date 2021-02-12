import logging
import traceback

from odoo import models, fields, tools, exceptions, _

from ..debug_logger import DebugLogger

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
        'Object ID', required=True,
        help='ID of object to test condition on')
    test_as_user_id = fields.Many2one('res.users')
    result = fields.Text(readonly=True)
    debug_log = fields.Html(readonly=True)

    def _get_record_internal(self):
        TestModel = self.env[self.condition_id.model_id.model]
        record = TestModel.browse(self.res_id)
        if not record.exists():
            raise exceptions.ValidationError(_(
                'Object (model: %(model)s; id: %(obj_id)s) not found'
            ) % {
                'model': self.condition_id.model_id.model,
                'obj_id': self.res_id,
            })
        return record

    def _get_record(self):
        record = self._get_record_internal()
        if self.test_as_user_id:
            record = record.with_user(self.test_as_user_id)
        return record

    def _adapt_result(self, result):
        if result is True:
            return _('Ok')
        if result is False:
            return _('Fail')
        if isinstance(result, Exception):
            return _('Error')
        return _('Unknown')

    def _compute_result(self, debug_log):
        cache = dict()
        record = self._get_record()
        if self.test_as_user_id:
            return self.condition_id.with_user(self.test_as_user_id).check(
                record, cache=cache, debug_log=debug_log)

        return self.condition_id.check(
            record, cache=cache, debug_log=debug_log)

    def _get_result(self, debug_log):
        try:
            with self.env.cr.savepoint():
                result = self._compute_result(debug_log)
        except Exception as exc:
            result = str(exc)
            self.condition_id._debug_log(
                debug_log,
                self._get_record_internal(),
                "<pre>%s</pre>" % traceback.format_exc())
        return self._adapt_result(result)

    def process(self):
        self.ensure_one()
        debug_log = DebugLogger()
        result = self._get_result(debug_log)
        self.write({
            'result': tools.ustr(result),
            'debug_log': debug_log.get_log_html(),
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'generic.condition.test_condition',
            'view_mode': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
            'context': dict(self.env.context),
        }
