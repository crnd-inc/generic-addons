from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError, UserError

from ..utils import str_to_datetime
from ..debug_logger import DebugLogger

import re
import traceback
import time
import datetime
import dateutil
from dateutil.relativedelta import relativedelta
from pytz import timezone

import logging
_logger = logging.getLogger(__name__)


class GenericCondition(models.Model):
    _name = "generic.condition"
    _inherit = [
        'mail.thread',
    ]
    _order = "sequence"
    _description = 'Generic Condition'
    _rec_name = 'name'

    # To add new type just override this method in subclass,
    # adding it after calling super
    def _get_selection_type(self):
        return [
            ('eval', _('Expression')),
            ('filter', _('Filter')),
            ('condition', _('Condition')),
            ('related_conditions', _('Related conditions')),
            ('date_diff', _('Date difference')),
            ('condition_group', _('Condition group')),
            ('simple_field', _('Simple field')),
            ('related_field', _('Related field')),
            ('current_user', _('Current user')),
            ('monetary_field', _('Monetary field')),
        ]

    def _get_selection_date_diff_uom(self):
        return [
            ('hours', _('Hours')),
            ('days', _('Days')),
            ('weeks', _('Weeks')),
            ('months', _('Months')),
            ('years', _('Years')),
        ]

    def _get_selection_date_diff_operator(self):
        return [
            ('=', '='),
            ('>', '>'),
            ('<', '<'),
            ('>=', '>='),
            ('<=', '<='),
            ('!=', '!='),
        ]

    def _get_selection_simple_field_number_operator(self):
        return [
            ('=', '='),
            ('>', '>'),
            ('<', '<'),
            ('>=', '>='),
            ('<=', '<='),
            ('!=', '!='),
        ]

    def _get_selection_simple_field_string_operator(self):
        return [
            ('=', '='),
            ('!=', '!='),
            ('set', _('Set')),
            ('not set', _('Not set')),
            ('contains', _('Contains')),
        ]

    def _get_selection_simple_field_string_operator_html(self):
        return [
            ('set', _('Set')),
            ('not set', _('Not set')),
            ('contains', _('Contains')),
        ]

    def _get_selection_simple_field_selection_operator(self):
        return [
            ('=', '='),
            ('!=', '!='),
            ('set', _('Set')),
            ('not set', _('Not set')),
        ]

    def _get_selection_related_field_operator(self):
        return [
            ('set', _('Set')),
            ('not set', _('Not set')),
            ('contains', _('Contains')),
        ]

    def _get_selection_date_diff_date_type(self):
        return [
            ('now', _('Current date')),
            ('field', _('Field')),
            ('date', _('Date')),
            ('datetime', _('Datetime')),
        ]

    def _get_selection_condition_condition_ids_operator(self):
        return [
            ('or', _('OR')),
            ('and', _('AND')),
        ]

    def _get_selection_condition_rel_record_operator(self):
        return [
            ('match', _('Match')),
            ('contains', _('Contains')),
        ]

    def _get_selection_monetary_field_operator(self):
        return [
            ('=', '='),
            ('>', '>'),
            ('<', '<'),
            ('>=', '>='),
            ('<=', '<='),
            ('!=', '!='),
        ]

    def _get_selection_currency_date_type(self):
        return [
            ('now', _('Current date')),
            ('field', _('Field')),
            ('date', _('Date'))
        ]

    @api.constrains('type', 'model_id', 'condition_condition_id')
    def _constrain_condition_condition_id(self):
        for record in self:
            if record.type != 'condition':
                continue
            if record.condition_condition_id.model_id != record.model_id:
                raise ValidationError(_(
                    "Incorrect Conditon field set for condition: %s[%s]"
                ) % (record.display_name, record.id))

    @api.constrains('type', 'model_id', 'condition_filter_id')
    def _constrain_condition_filter_id(self):
        for record in self:
            if record.type != 'filter':
                continue
            if record.condition_filter_id.model_id != record.model_id.model:
                raise ValidationError(_(
                    "Incorrect Filter field set for condition: %s[%s]"
                ) % (record.display_name, record.id))

    @api.constrains('type', 'model_id', 'condition_condition_ids')
    def _constrain_condition_group(self):
        for record in self:
            if record.type != 'condition_group':
                continue
            for c in record.condition_condition_ids:
                if c.model_id != record.model_id:
                    raise ValidationError(_(
                        "Incorrect Condition (condition group) selected!\n"
                        "Base condition: %s[%s]\n"
                        "Condition with wrong model: %s[%s]"
                    ) % (record.display_name, record.id,
                         c.display_name, c.id))

    @api.constrains('type', 'model_id', 'condition_rel_field_id')
    def _constrain_condition_rel_field_id(self):
        for cond in self:
            if cond.type != 'related_conditions':
                continue
            rel_field_id = cond.condition_rel_field_id
            if rel_field_id:
                rel_field_model_id = cond.condition_rel_field_id.model_id
                if rel_field_model_id != cond.model_id:
                    raise ValidationError(
                        _('Wrong Related Field / Based on combination'))
        return True

    color = fields.Integer()
    name = fields.Char(required=True, index=True, translate=True,
                       track_visibility='onchange')
    type = fields.Selection(
        '_get_selection_type', default='filter',
        index=True, required=True, track_visibility='onchange')
    model_id = fields.Many2one(
        'ir.model', 'Based on model', required=True, index=True)
    based_on = fields.Char(
        related='model_id.model', readonly=True, index=True, store=True,
        related_sudo=True, track_visibility='onchange')
    sequence = fields.Integer(
        index=True, default=10, track_visibility='onchange')
    active = fields.Boolean(
        index=True, default=True, track_visibility='onchange')
    invert = fields.Boolean('Invert (Not)', track_visibility='onchange')
    with_sudo = fields.Boolean(default=False, track_visibility='onchange')
    enable_caching = fields.Boolean(
        default=True,
        help='If set, then condition result for a specific object will be '
             'cached during one condition chain call. '
             'This may speed up condition processing.',
        track_visibility='onchange')
    description = fields.Text(translate=True)

    # Condition type 'eval' params
    condition_eval = fields.Char(
        'Condition (eval)', required=False, track_visibility='onchange',
        help="Python expression. 'obj' are present in context.")

    # Condition type 'filter' params
    condition_filter_id = fields.Many2one(
        'ir.filters', string='Condition (filter)', auto_join=True,
        ondelete='restrict', track_visibility='onchange',
        help="User filter to be applied by this condition.")

    # Condition type 'condition' params
    condition_condition_id = fields.Many2one(
        'generic.condition', 'Condition (condition)',
        ondelete='restrict', track_visibility='onchange', auto_join=True,
        help='Link to another condition. Usualy used to get '
             'inversed condition')

    # Condition type 'condition_group' params
    condition_condition_ids = fields.Many2many(
        'generic.condition',
        'generic_condition__condition_group__rel',
        'parent_condition_id', 'sub_condition_id',
        string='Condition (condition group)',
        track_visibility='onchange', auto_join=True,
        help='Check set of other conditions')
    condition_condition_ids_operator = fields.Selection(
        '_get_selection_condition_condition_ids_operator', default='and',
        string='Condition (condition group): operator',
        track_visibility='onchange')

    # Condition type 'current_user' params
    condition_user_user_field_id = fields.Many2one(
        'ir.model.fields', 'User Field',
        ondelete='restrict',
        domain=[('ttype', 'in', ('many2one', 'one2many', 'many2many')),
                ('relation', '=', 'res.users')],
        track_visibility='onchange',
        help='Field in object being checked, that points to user.')

    # Condition type 'related_conditions' params
    condition_rel_field_id = fields.Many2one(
        'ir.model.fields', 'Related Field',
        ondelete='restrict', auto_join=True,
        domain=[('ttype', 'in', ('many2one', 'one2many', 'many2many'))],
        track_visibility='onchange')
    condition_rel_field_id_model_id = fields.Many2one(
        'ir.model', compute='_compute_condition_rel_field_id_model_id',
        compute_sudo=True, string='Related field: model', readonly=True,
        track_visibility='onchange')
    condition_rel_record_operator = fields.Selection(
        '_get_selection_condition_rel_record_operator',
        'Related record operator', default='match',
        help='Choose way related record will be checked:\n'
             '- Match: return True if all filtered records match condition.\n'
             '- Contains: return True if at least one of filtered records '
             'match \'check\' conditions',
        track_visibility='onchange')
    condition_rel_filter_conditions = fields.Many2many(
        'generic.condition',
        'generic_condition_filter_conds',
        'parent_id', 'child_id', ondelete='restrict', auto_join=True,
        string='Related filter conditions',
        help="Used together with Related Field. "
             "These conditions are used to filter related items that "
             "will be checked by 'Related check conditions'. "
             "If this conditions evaluates to False for some object, "
             "that this object will not be checked",
        track_visibility='onchange')
    condition_rel_filter_conditions_operator = fields.Selection(
        '_get_selection_condition_condition_ids_operator', default='and',
        string='Related filter conditions operator',
        track_visibility='onchange')
    condition_rel_conditions = fields.Many2many(
        'generic.condition',
        'generic_condition_check_conds',
        'parent_id', 'child_id', ondelete='restrict', auto_join=True,
        string='Related check conditions',
        help="Used together with Related Field. "
             "These conditions will be used to check objects "
             "that passed filter conditions. "
             "And result of these related conditions will be used as result",
        track_visibility='onchange')
    condition_rel_conditions_operator = fields.Selection(
        '_get_selection_condition_condition_ids_operator', default='and',
        string='Related check conditions operator',
        track_visibility='onchange')

    # Date difference fields: start date
    condition_date_diff_date_start_type = fields.Selection(
        '_get_selection_date_diff_date_type',
        string='Date start type', default='now', track_visibility='onchange')
    condition_date_diff_date_start_field = fields.Many2one(
        'ir.model.fields', 'Date start field', ondelete='restrict',
        domain=[('ttype', 'in', ('date', 'datetime'))],
        track_visibility='onchange')
    condition_date_diff_date_start_date = fields.Date(
        'Date start', default=fields.Date.today, track_visibility='onchange')
    condition_date_diff_date_start_datetime = fields.Datetime(
        'Date start', default=fields.Datetime.now, track_visibility='onchange')

    # Date difference fields: end date
    condition_date_diff_date_end_type = fields.Selection(
        '_get_selection_date_diff_date_type',
        string='Date end type', default='now', track_visibility='onchange')
    condition_date_diff_date_end_field = fields.Many2one(
        'ir.model.fields', 'Date end field', ondelete='restrict',
        domain=[('ttype', 'in', ('date', 'datetime'))],
        track_visibility='onchange')
    condition_date_diff_date_end_date = fields.Date(
        'Date end', default=fields.Date.today, track_visibility='onchange')
    condition_date_diff_date_end_datetime = fields.Datetime(
        'Date end', default=fields.Datetime.now, track_visibility='onchange')

    # Date difference fields: check rules
    condition_date_diff_operator = fields.Selection(
        '_get_selection_date_diff_operator',
        string='Date diff operator', track_visibility='onchange')
    condition_date_diff_uom = fields.Selection(
        '_get_selection_date_diff_uom',
        string='Date diff UoM',
        help='Choose Unit of Measurement for date diff here',
        track_visibility='onchange')
    condition_date_diff_value = fields.Integer('Date diff value')
    condition_date_diff_absolute = fields.Boolean(
        'Absolute', default=False,
        help='If checked, then absolute date difference will be checked. '
             '(date difference will be positive always)',
        track_visibility='onchange')

    # Simple field conditions
    condition_simple_field_field_id = fields.Many2one(
        'ir.model.fields', 'Check field', ondelete='restrict',
        domain=[('ttype', 'in', ('boolean', 'char', 'text',
                                 'html', 'float',
                                 'integer', 'selection'))],
        track_visibility='onchange')
    condition_simple_field_type = fields.Selection(
        related='condition_simple_field_field_id.ttype',
        related_sudo=True, string='Field type', readonly=True,
        track_visibility='onchange')
    condition_simple_field_value_boolean = fields.Selection(
        [('true', 'True'), ('false', 'False')], 'Value',
        track_visibility='onchange')
    condition_simple_field_value_char = fields.Char(
        'Value', track_visibility='onchange')
    condition_simple_field_value_float = fields.Float(
        'Value', track_visibility='onchange')
    condition_simple_field_value_integer = fields.Integer(
        'Value', track_visibility='onchange')
    condition_simple_field_value_selection = fields.Char(
        'Value', track_visibility='onchange')
    condition_simple_field_selection_operator = fields.Selection(
        '_get_selection_simple_field_selection_operator', 'Operator',
        track_visibility='onchange')
    condition_simple_field_number_operator = fields.Selection(
        '_get_selection_simple_field_number_operator', 'Operator',
        track_visibility='onchange')
    condition_simple_field_string_operator = fields.Selection(
        '_get_selection_simple_field_string_operator', 'Operator',
        track_visibility='onchange')
    condition_simple_field_string_operator_html = fields.Selection(
        '_get_selection_simple_field_string_operator_html', 'Operator',
        track_visibility='onchange')
    condition_simple_field_string_operator_icase = fields.Boolean(
        'Case insensitive', track_visibility='onchange')
    condition_simple_field_string_operator_regex = fields.Boolean(
        'Regular expression', track_visibility='onchange')

    # Related field conditions
    condition_related_field_field_id = fields.Many2one(
        'ir.model.fields', 'Check field', ondelete='restrict',
        domain=[('ttype', 'in', ('many2one', 'many2many'))])
    condition_related_field_model = fields.Char(
        string='Related Model',
        related='condition_related_field_field_id.relation',
        related_sudo=True, readonly=True,
        help="Technical name of related field's model",
        track_visibility='onchange')
    condition_related_field_operator = fields.Selection(
        '_get_selection_related_field_operator', 'Operator',
        track_visibility='onchange')
    condition_related_field_value_id = fields.Integer(
        'Value', track_visibility='onchange')

    # Monetary field conditions
    # Value monetary fields
    condition_monetary_field_id = fields.Many2one(
        'ir.model.fields', 'Field', ondelete='restrict',
        domain=[('ttype', '=', 'monetary')], track_visibility='onchange')
    condition_monetary_currency_field_id = fields.Many2one(
        'ir.model.fields', 'Currency', ondelete='restrict',
        domain=[('ttype', '=', 'many2one'),
                ('relation', '=', 'res.currency')],
        help="Field with currency for field being checked",
        track_visibility='onchange')

    # Monetary fields: check rules
    condition_monetary_operator = fields.Selection(
        '_get_selection_monetary_field_operator',
        string='Operator', track_visibility='onchange')
    condition_monetary_value = fields.Monetary(
        'Value',
        currency_field='condition_monetary_value_currency_id',
        track_visibility='onchange')
    condition_monetary_value_currency_id = fields.Many2one(
        'res.currency', 'Currency', ondelete='restrict',
        track_visibility='onchange')
    # Monetary fields: currency date
    condition_monetary_curency_date_type = fields.Selection(
        '_get_selection_currency_date_type',
        string='Type', default='now', track_visibility='onchange')
    condition_monetary_curency_date_field_id = fields.Many2one(
        'ir.model.fields', 'Field', ondelete='restrict',
        domain=[('ttype', 'in', ('date', 'datetime'))],
        track_visibility='onchange')
    condition_monetary_curency_date_date = fields.Date(
        'Date', default=fields.Date.today, track_visibility='onchange')

    @api.model
    def default_get(self, field_names):
        """ If there is no default model id but default based on, then
            search for defautl model and make it default
        """
        if not self.env.context.get('default_model_id') and \
                self.env.context.get('default_based_on'):
            based_on = self.env.context['default_based_on']
            model = self.env['ir.model'].sudo().search(
                [('model', '=', based_on)], limit=1)
            if model:
                xself = self.with_context(default_model_id=model.id)
                return super(GenericCondition, xself).default_get(field_names)
        return super(GenericCondition, self).default_get(field_names)

    @api.multi
    @api.depends('condition_rel_field_id')
    def _compute_condition_rel_field_id_model_id(self):
        """ Sets value for condition_rel_field_id_model_id
            when condition_rel_field_id changed
        """
        for cond in self:
            if cond.sudo().condition_rel_field_id:
                field = cond.sudo().condition_rel_field_id
                rel_model = self.env['ir.model'].sudo().search(
                    [('model', '=', field.relation)], limit=1)
                cond.condition_rel_field_id_model_id = rel_model

    # signature check_<type> where type is condition type
    def check_filter(self, obj, cache=None, debug_log=None):
        """ Check object with conditions filter applied
        """
        Model = self.env[self.sudo().model_id.model]

        filter_obj = self.sudo().condition_filter_id
        domain = [('id', '=', obj.id)] + safe_eval(filter_obj.domain)

        ctx = self.env.context.copy()
        ctx.update(safe_eval(filter_obj.context, ctx))
        return bool(Model.with_context(ctx).search(domain, count=True))

    # signature check_<type> where type is condition type
    def check_eval(self, obj, cache=None, debug_log=None):
        try:
            res = bool(safe_eval(self.condition_eval, dict(self.env.context)))
        except Exception:
            condition_name = self.name_get()[0][1]
            obj_name = "%s [id:%s] (%s)" % (self.sudo().model_id.model,
                                            obj.id,
                                            obj.sudo().name_get()[0][1])
            _logger.error(
                "Error was cauht when checking condition %s on document %s. "
                "condition expression:\n%s\n", condition_name, obj_name,
                self.condition_eval, exc_info=True)
            raise ValidationError(
                _("Checking condition %s on document %s caused error. "
                  "Notify administrator to fix it.\n\n---\n"
                  "%s") % (condition_name, obj_name, traceback.format_exc()))
        return res

    # signature check_<type> where type is condition type
    def check_condition(self, obj, cache=None, debug_log=None):
        return self.condition_condition_id.check(
            obj, cache=cache, debug_log=debug_log)

    # signature check_<type> where type is condition type
    def check_condition_group(self, obj, cache=None, debug_log=None):
        return self.condition_condition_ids.check(
            obj, operator=self.condition_condition_ids_operator,
            cache=cache, debug_log=debug_log)

    # signature check_<type> where type is condition type
    def check_related_conditions(self, obj, cache=None, debug_log=None):
        """ This check will return OK if all related objects that passes
            filter condition also passes check condition.

            Same as filter out all related objects that passes
            filter condition, and then check them with check conditions
        """
        # Get related field value.
        field = self.condition_rel_field_id.sudo()
        related = obj[field.name]
        if not related:
            return False

        # Group condition by operator
        filter_operator = self.condition_rel_filter_conditions_operator
        operator = self.condition_rel_conditions_operator

        # Fallback to default 'and'. (For backward compatability)
        if not filter_operator:
            filter_operator = 'and'
        if not operator:
            operator = 'and'

        matched = False
        for rel_rec in related:
            # Skip record that does not match filter conditions
            if (self.condition_rel_filter_conditions and
                    not self.condition_rel_filter_conditions.check(
                        rel_rec, operator=filter_operator,
                        cache=cache, debug_log=debug_log)):
                continue

            # check if record match 'check' conditions
            if not self.condition_rel_conditions.check(
                    rel_rec, operator=operator,
                    cache=cache, debug_log=debug_log):
                # If 'rel record operator' is 'match' we could just return
                # False, because it requires all record to match 'check'
                # conditions and we have found first record that does not match
                if self.condition_rel_record_operator == 'match':
                    return False

            else:  # check returned True
                if self.condition_rel_record_operator == 'contains':
                    # If check conditions passed for this record and
                    # 'rel record operator is 'contains', we can
                    # return True, because we have found first record
                    # that match 'check' conditions. all other recors don't
                    # matter
                    return True
                elif self.condition_rel_record_operator == 'match':
                    # mark that atleast one record matched. This is used by
                    # 'match' rel_record_operator. if all records match 'check'
                    # conditions, then we shoudl know about it after this loop
                    matched = True

        if self.condition_rel_record_operator == 'match' and matched:
            # All records match 'check' conditions
            return True

        # Here we return False, because for 'contains' operator,
        # we have no found any record that match 'check' conditions,
        # and for 'match' operator, we have nothing to check (all records
        # filtered by 'filter' conditions).
        return False

    def helper_date_diff_get_date(self, date_type, obj):
        """ Get date value of specified type for specified object

            :param str date_type: type of date to get value for.
                                  Possible values:
                                      - 'start'
                                      - 'end'
            :param Recordset obj: object to get date from
        """
        if date_type not in ('start', 'end'):
            raise AssertionError("Date type not in (start,stop)")

        date_source = self['condition_date_diff_date_%s_type' % date_type]

        if date_source == 'now':
            return datetime.datetime.now()
        elif date_source == 'date':
            date = self['condition_date_diff_date_%s_date' % date_type]
            return str_to_datetime('date', date)
        elif date_source == 'datetime':
            date = self['condition_date_diff_date_%s_datetime' % date_type]
            return str_to_datetime('datetime', date)
        elif date_source == 'field':
            field_name = 'condition_date_diff_date_%s_field' % date_type
            field = self.sudo()[field_name]
            return str_to_datetime(field.ttype, obj[field.name])

    # signature check_<type> where type is condition type
    def check_current_user(self, obj, cache=None, debug_log=None):
        field = self.sudo().condition_user_user_field_id
        obj_value = obj[field.name]

        if obj_value and self.env.user in obj_value:
            return True
        return False

    # signature check_<type> where type is condition type
    def check_date_diff(self, obj, cache=None, debug_log=None):
        """ Check date diff

            If at least one of dates not set, than return False
        """
        date_start = self.helper_date_diff_get_date('start', obj)
        date_end = self.helper_date_diff_get_date('end', obj)

        # if at leas one field not set, fail
        if not date_start or not date_end:
            self._debug_log(
                debug_log, obj,
                "Date start (%s) or date end (%s) not set. "
                "Returning False" % (date_start, date_end))
            return False

        # if dates not in correct order then swap them
        if self.condition_date_diff_absolute and date_end < date_start:
            date_start, date_end = date_end, date_start

        # delta betwen two dates
        delta = relativedelta(date_end, date_start)

        uom = self.condition_date_diff_uom
        value = self.condition_date_diff_value
        operator = self.condition_date_diff_operator

        # used for operators '==' and '!='
        uom_map = {
            'hours': lambda d1, d2, dt: round((d1 - d2).total_seconds() / 60.0 / 60.0),  # noqa
            'days': lambda d1, d2, dt: (d1 - d2).days,
            'weeks': lambda d1, d2, dt: round(uom_map['days'](d1, d2, dt) / 7.0),  # noqa
            'months': lambda d1, d2, dt: dt.months + dt.years * 12,
            'years': lambda d1, d2, dt: dt.years,
        }

        operator_map = {
            '>': lambda a, b: a > b,
            '<': lambda a, b: a < b,
            '>=': lambda a, b: a >= b,
            '<=': lambda a, b: a <= b,
        }

        # Special cases for '=' and '!=' to assume that following dates
        # are same:
        # 2017-04-03 12:31:44 ~ 2017-04-03 12:31:15
        if operator == '=':
            return uom_map[uom](date_end, date_start, delta) == value
        elif operator == '!=':
            return uom_map[uom](date_end, date_start, delta) != value
        elif operator in operator_map:
            # EX: date_end - date_start (>|>=|<|<=) 2 years
            #     equal to
            #     date_start + 2 year (>|>=|<|<=) date_end
            return operator_map[operator](
                date_end,
                date_start + relativedelta(**{uom: value})
            )

    def helper_check_simple_field_number(self, obj_value):
        operator_map = {
            '=': lambda a, b: a == b,
            '>': lambda a, b: a > b,
            '<': lambda a, b: a < b,
            '>=': lambda a, b: a >= b,
            '<=': lambda a, b: a <= b,
            '!=': lambda a, b: a != b,
        }

        operator = self.condition_simple_field_number_operator

        if self.condition_simple_field_type == 'float':
            reference_value = self.condition_simple_field_value_float
        elif self.condition_simple_field_type == 'integer':
            reference_value = self.condition_simple_field_value_integer

        return operator_map[operator](obj_value, reference_value)

    def helper_check_simple_field_string_regex_params(self, operator):
        reference_value = self.condition_simple_field_value_char
        is_regex = self.condition_simple_field_string_operator_regex

        # Compute regex flags
        re_flags = re.UNICODE
        if self.condition_simple_field_string_operator_icase:
            re_flags |= re.IGNORECASE

        # if not regex, do re.escape
        if not is_regex and operator in ('=', '!='):
            reference_value = u'^%s$' % re.escape(reference_value)
        elif not is_regex and operator == 'contains':
            reference_value = re.escape(
                reference_value)

        return reference_value, re_flags

    def helper_check_simple_field_string(self, obj_value):
        operator = self.condition_simple_field_string_operator
        if self.condition_simple_field_type == 'html':
            operator = self.condition_simple_field_string_operator_html

            # Summernote web editor set this value as default, so, if user does
            # not change it, this value goes to odoo's python code.
            # Here we treat this value as empty field placeholder
            if obj_value == '<p><br></p>':
                obj_value = False

        # Simple operators
        if operator == 'set':
            return bool(obj_value)
        elif operator == 'not set':
            return not bool(obj_value)

        # Get reference value as regex and regex flags
        reference_value, re_flags = (
            self.helper_check_simple_field_string_regex_params(operator)
        )

        # Do everything via regex
        if obj_value and operator == '=':
            return bool(
                re.match(
                    reference_value,
                    obj_value,
                    re_flags))
        elif obj_value and operator == '!=':
            return not bool(
                re.match(
                    reference_value,
                    obj_value,
                    re_flags))
        elif not obj_value and operator == '!=':
            # False != reference_value
            return True
        elif obj_value and operator == 'contains':
            return bool(
                re.search(
                    reference_value,
                    obj_value,
                    re_flags))

    def helper_check_simple_field_boolean(self, obj_value):
        reference_value = self.condition_simple_field_value_boolean
        if reference_value == 'true' and obj_value:
            return True
        if reference_value == 'false' and not obj_value:
            return True
        return False

    def helper_check_simple_field_selection(self, obj_value):
        operator = self.condition_simple_field_selection_operator
        reference_value = self.condition_simple_field_value_selection

        # Simple operators
        if operator == 'set':
            return bool(obj_value)
        elif operator == 'not set':
            return not bool(obj_value)
        elif operator == '=':
            return obj_value == reference_value
        elif operator == '!=':
            return obj_value != reference_value

    # signature check_<type> where type is condition type
    def check_simple_field(self, obj, cache=None, debug_log=None):
        """ Check value of simple field of object
        """
        field = self.sudo().condition_simple_field_field_id
        value = obj[field.name]

        if field.ttype in ('integer', 'float'):
            return self.helper_check_simple_field_number(value)
        elif field.ttype in ('char', 'text', 'html'):
            return self.helper_check_simple_field_string(value)
        elif field.ttype == 'boolean':
            return self.helper_check_simple_field_boolean(value)
        elif field.ttype == 'selection':
            return self.helper_check_simple_field_selection(value)
        raise NotImplementedError()

    # signature check_<type> where type is condition type
    def check_related_field(self, obj, cache=None, debug_log=None):
        operator = self.condition_related_field_operator
        field = self.sudo().condition_related_field_field_id
        obj_value = obj[field.name]

        # Simple operators
        if operator == 'set':
            return bool(obj_value)
        elif operator == 'not set':
            return not bool(obj_value)
        elif obj_value and operator == 'contains':
            reference_value_id = self.condition_related_field_value_id
            return reference_value_id in obj_value.ids

        return False

    def helper_check_monetary_field_date(self, obj):
        # Compute accounting date
        if self.condition_monetary_curency_date_type == 'date':
            return self.condition_monetary_curency_date_date
        elif self.condition_monetary_curency_date_type == 'field':
            currency_date_field = (
                self.condition_monetary_curency_date_field_id.sudo())
            return obj[currency_date_field.name]
        return fields.Datetime.now()

    # signature check_<type> where type is condition type
    def check_monetary_field(self, obj, cache=None, debug_log=None):
        field = self.condition_monetary_field_id.sudo()
        currency_field = self.condition_monetary_currency_field_id
        date = self.helper_check_monetary_field_date(obj)

        operator_map = {
            '=': lambda a, b: a == b,
            '>': lambda a, b: a > b,
            '<': lambda a, b: a < b,
            '>=': lambda a, b: a >= b,
            '<=': lambda a, b: a <= b,
            '!=': lambda a, b: a != b,
        }
        operator = operator_map[self.condition_monetary_operator]

        # Object value
        obj_val = obj[field.name]
        obj_val_currency = obj[currency_field.name]

        # Reference value
        reference_value = self.condition_monetary_value
        reference_currency = self.condition_monetary_value_currency_id

        # Object value in reference currency
        test_value = obj_val_currency.with_context(date=date).compute(
            obj_val, reference_currency)

        return operator(test_value, reference_value)

    def _debug_log(self, log, obj, msg):
        self.ensure_one()
        if isinstance(log, DebugLogger):
            log.log(self, obj, msg)

    def _check(self, obj, cache=None, debug_log=None):
        """ Checks one condition for a specific object
        """
        self.ensure_one()
        if obj._name != self.based_on:
            raise UserError(_(
                "Generic conditions misconfigured!\n"
                "object's model and condition's model does not match:\n"
                "\tcondition: %s [%d]"
                "\tobject: %s [%d]"
                "\tobject's model: %s\n"
                "\tcondition's model: %s\n") % (
                    self.display_name,
                    self.id,
                    obj.display_name,
                    obj.id,
                    obj._name,
                    self.based_on,
                ))

        self._debug_log(debug_log, obj, "Computing...")

        # Is sudo condition?
        condition = self
        if self.with_sudo:
            condition = self.sudo()
            obj = obj.sudo()
            self._debug_log(
                debug_log, obj, "Using sudo")

        # generate cache_key
        cache_key = (condition.id, obj.id)

        # check cache
        if (condition.enable_caching and
                cache is not None and
                cache_key in cache):
            self._debug_log(
                debug_log, obj,
                "Using cached result: %s" % cache[cache_key])
            return cache[cache_key]

        # get condition's check method
        try:
            check_method = getattr(condition, 'check_%s' % condition.type)
        except AttributeError:
            _logger.error(
                "Condition's check method not found.\n"
                "\tcondition: %s[%d]"
                "\tcondition type: %s",
                condition.name, condition.id, condition.type, exc_info=True)
            raise

        # calculate condition
        try:
            res = check_method(obj, cache=cache, debug_log=debug_log)
        except Exception:
            msg = _("Error caught while evaluating condition %s[%d]"
                    "") % (condition.name, condition.id,)
            _logger.error(msg, exc_info=True)
            raise

        # Invert result if required
        res = (not res) if condition.invert else res

        # set cache
        if condition.enable_caching and cache is not None:
            cache[cache_key] = res

        self._debug_log(
            debug_log, obj,
            "Computed result: %s" % res)
        return res

    @api.model
    def _prepare_object_context(self, obj):
        """ Prepare context to check conditions for object object

            This method may be used as hook, by other modules
            to fill evaluation context with extra values
        """
        return {
            'obj': obj,
            'record': obj,
            'env': self.env,
            'model': self.env[obj._name],
            'uid': self._uid,
            'user': self.env.user,
            'time': time,
            'datetime': datetime,
            'dateutil': dateutil,
            'timezone': timezone,
        }

    @api.multi
    def check(self, obj, operator='and', cache=None, debug_log=None):
        """ Checks if specified conditions satisfied

            :param obj: browse_record of object to be checked with conditions
            :param operator: how to join conditions. one of ('and', 'or'),
                             default: 'and'
        """
        if operator not in ('and', 'or'):
            raise AssertionError("Operator must be in ('and', 'or')")

        if not obj:
            raise UserError(_("Cannot check conditions for empty recordset"))

        cache = {} if cache is None else cache

        ctx = self._prepare_object_context(obj)

        if not self:
            # if there are no conditions, assume check is ok
            return True

        # Do actual condition processing
        for cond in self:
            res = cond.with_context(ctx)._check(
                obj, cache=cache, debug_log=debug_log)
            if operator == 'and' and not res:
                # if operator is and, then fail on first failed condition
                return False
            elif operator == 'or' and res:
                # if operator is or, then return ok on first successful check
                return True

        if operator == 'and':
            # there are no failed checks, so return ok
            return True
        elif operator == 'or':
            # there are no successful check, so all checks are failed, return
            # fail
            return False

    def action_show_test_wizard(self):
        self.ensure_one()
        action = self.env.ref(
            'generic_condition'
            '.action_generic_condition_test_wizard_view').read()[0]
        action['context'] = dict(
            self.env.context,
            default_condition_id=self.id)
        return action
