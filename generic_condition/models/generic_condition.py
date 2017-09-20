# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.tools.safe_eval import safe_eval
from openerp.exceptions import ValidationError, UserError
import datetime
from dateutil.relativedelta import relativedelta

from ..utils import str_to_datetime

import re
import traceback
import time
import datetime
import dateutil
from pytz import timezone

import logging
_logger = logging.getLogger(__name__)


class GenericCondition(models.Model):
    _name = "generic.condition"
    _order = "sequence"
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

    @api.constrains('condition_rel_field_id', 'model_id')
    def _check_condition_rel_field_id(self):
        for cond in self:
            rel_field_id = cond.condition_rel_field_id
            if rel_field_id:
                rel_field_model_id = cond.condition_rel_field_id.model_id
                if rel_field_model_id != cond.model_id:
                    raise ValidationError(
                        _('Wrong Related Field / Based on combination'))
        return True

    color = fields.Integer()
    name = fields.Char(required=True, index=True)
    type = fields.Selection(
        '_get_selection_type', default='filter',
        index=True, required=True)
    model_id = fields.Many2one(
        'ir.model', 'Based on model', required=True, index=True)
    based_on = fields.Char(
        related='model_id.model', readonly=True, index=True, store=True)
    sequence = fields.Integer(index=True, default=10)
    active = fields.Boolean(index=True, default=True)
    invert = fields.Boolean('Invert (Not)')
    enable_caching = fields.Boolean(
        default=True,
        help='If set, then condition result for a specific object will be '
             'cached during one condition chain call. '
             'This may speed up condition processing.')
    condition_eval = fields.Char(
        'Condition (eval)', required=False, track_visibility='onchange',
        help="Python expression. 'obj' are present in context.")
    condition_filter_id = fields.Many2one(
        'ir.filters', string='Condition (filter)', auto_join=True,
        ondelete='restrict', track_visibility='onchange',
        help="User filter to be applied by this condition.")
    condition_condition_id = fields.Many2one(
        'generic.condition', 'Condition (condition)',
        ondelete='restrict', track_visibility='onchange', auto_join=True,
        help='Link to another condition. Usualy used to get '
             'inversed condition')

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

    # Related conditions
    condition_rel_field_id = fields.Many2one(
        'ir.model.fields', 'Related Field',
        ondelete='restrict', auto_join=True,
        domain=[('ttype', 'in', ('many2one', 'one2many', 'many2many'))])
    condition_rel_field_id_model_id = fields.Many2one(
        'ir.model', compute='_compute_condition_rel_field_id_model_id',
        string='Related field: model', readonly=True)
    condition_rel_record_operator = fields.Selection(
        '_get_selection_condition_rel_record_operator',
        'Related record operator', default='match',
        help='Choose way related record will be checked:\n'
             '- Match: return True if all filtered records match condition.\n'
             '- Contains: return True if at least one of filtered records '
             'match \'check\' conditions')
    condition_rel_filter_conditions = fields.Many2many(
        'generic.condition',
        'generic_condition_filter_conds',
        'parent_id', 'child_id', ondelete='restrict', auto_join=True,
        string='Related filter conditions',
        help="Used together with Related Field. "
             "These conditions are used to filter related items that"
             "will be checked by 'Related check conditions'. "
             "If this conditions evaluates to False for some object, "
             "that this object will not be checked")
    condition_rel_filter_conditions_operator = fields.Selection(
        '_get_selection_condition_condition_ids_operator', default='and',
        string='Related filter conditions operator',
        track_visibility='onchange')
    condition_rel_conditions = fields.Many2many(
        'generic.condition',
        'generic_condition_check_conds',
        'parent_id', 'child_id', ondelete='restrict', auto_join=True,
        string='Related check conditions',
        help="Used together with Related Field"
             "These conditions will be used to check objects "
             "that passed filter conditions."
             "And result of these related conditions will be used as result")
    condition_rel_conditions_operator = fields.Selection(
        '_get_selection_condition_condition_ids_operator', default='and',
        string='Related check conditions operator',
        track_visibility='onchange')

    # Date difference fields: start date
    condition_date_diff_date_start_type = fields.Selection(
        '_get_selection_date_diff_date_type',
        string='Date start type', default='now')
    condition_date_diff_date_start_field = fields.Many2one(
        'ir.model.fields', 'Date start field', ondelete='restrict',
        domain=[('ttype', 'in', ('date', 'datetime'))])
    condition_date_diff_date_start_date = fields.Date(
        'Date start', default=fields.Date.today)
    condition_date_diff_date_start_datetime = fields.Datetime(
        'Date start', default=fields.Datetime.now)

    # Date difference fields: end date
    condition_date_diff_date_end_type = fields.Selection(
        '_get_selection_date_diff_date_type',
        string='Date end type', default='now')
    condition_date_diff_date_end_field = fields.Many2one(
        'ir.model.fields', 'Date end field', ondelete='restrict',
        domain=[('ttype', 'in', ('date', 'datetime'))])
    condition_date_diff_date_end_date = fields.Date(
        'Date end', default=fields.Date.today)
    condition_date_diff_date_end_datetime = fields.Datetime(
        'Date end', default=fields.Datetime.now)

    # Date difference fields: check rules
    condition_date_diff_operator = fields.Selection(
        '_get_selection_date_diff_operator',
        string='Date diff operator')
    condition_date_diff_uom = fields.Selection(
        '_get_selection_date_diff_uom',
        string='Date diff UoM',
        help='Choose Unit of Measurement for date diff here')
    condition_date_diff_value = fields.Integer('Date diff value')
    condition_date_diff_absolute = fields.Boolean(
        'Absolute', default=False,
        help='If checked, then absolute date difference will be checked. '
             '(date difference will be positive always)')

    # Simple field conditions
    condition_simple_field_field_id = fields.Many2one(
        'ir.model.fields', 'Check field', ondelete='restrict',
        domain=[('ttype', 'in', ('boolean', 'char', 'float',
                                 'integer', 'selection'))])
    condition_simple_field_type = fields.Selection(
        related='condition_simple_field_field_id.ttype',
        string='Field type', readonly=True)
    condition_simple_field_value_boolean = fields.Selection(
        [('true', 'True'), ('false', 'False')], 'Value')
    condition_simple_field_value_char = fields.Char('Value')
    condition_simple_field_value_float = fields.Float('Value')
    condition_simple_field_value_integer = fields.Integer('Value')
    condition_simple_field_value_selection = fields.Char('Value')
    condition_simple_field_selection_operator = fields.Selection(
        '_get_selection_simple_field_selection_operator', 'Operator')
    condition_simple_field_number_operator = fields.Selection(
        '_get_selection_simple_field_number_operator', 'Operator')
    condition_simple_field_string_operator = fields.Selection(
        '_get_selection_simple_field_string_operator', 'Operator')
    condition_simple_field_string_operator_icase = fields.Boolean(
        'Case insensitive')
    condition_simple_field_string_operator_regex = fields.Boolean(
        'Regular expression')

    # Related field conditions
    condition_related_field_field_id = fields.Many2one(
        'ir.model.fields', 'Check field', ondelete='restrict',
        domain=[('ttype', 'in', ('many2one', 'many2many'))])
    condition_related_field_model = fields.Char(
        string='Related Model',
        related='condition_related_field_field_id.relation',
        help="Technical name of related field's model",
        readonly=True)
    condition_related_field_operator = fields.Selection(
        '_get_selection_related_field_operator', 'Operator')
    condition_related_field_value_id = fields.Integer('Value')

    @api.model
    def default_get(self, fields):
        """ If there is no default model id but default based on, then
            search for defautl model and make it default
        """
        if not self.env.context.get('default_model_id') and \
                self.env.context.get('default_based_on'):
            based_on = self.env.context['default_based_on']
            model_id = self.env['ir.model'].search(
                [('model', '=', based_on)], limit=1)
            if model_id:
                xself = self.with_context(default_model_id=model_id.id)
                return super(GenericCondition, xself).default_get(fields)
        return super(GenericCondition, self).default_get(fields)

    @api.multi
    @api.depends('condition_rel_field_id')
    def _compute_condition_rel_field_id_model_id(self):
        """ Sets value for condition_rel_field_id_model_id
            when condition_rel_field_id changed
        """
        for cond in self:
            if cond.condition_rel_field_id:
                field = cond.condition_rel_field_id
                rel_model_id = self.env['ir.model'].search(
                    [('model', '=', field.relation)], limit=1)
                cond.condition_rel_field_id_model_id = rel_model_id

    # signature check_<type> where type is condition type
    def check_filter(self, obj, cache=None):
        """ Check object with conditions filter applied
        """
        Model = self.env[self.model_id.model]

        filter_obj = self.condition_filter_id
        domain = [('id', '=', obj.id)] + safe_eval(filter_obj.domain)

        ctx = self.env.context.copy()
        ctx.update(safe_eval(filter_obj.context, ctx))
        return bool(Model.with_context(ctx).search(domain, count=True))

    # signature check_<type> where type is condition type
    def check_eval(self, obj, cache=None):
        try:
            res = bool(safe_eval(self.condition_eval, dict(self.env.context)))
        except:
            condition_name = self.name_get()[0][1]
            obj_name = "%s [id:%s] (%s)" % (self.model_id.model,
                                            obj.id,
                                            obj.name_get()[0][1])
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
    def check_condition(self, obj, cache=None):
        return self.condition_condition_id.check(obj, cache=cache)

    # signature check_<type> where type is condition type
    def check_condition_group(self, obj, cache=None):
        return self.condition_condition_ids.check(
            obj, operator=self.condition_condition_ids_operator, cache=cache)

    # signature check_<type> where type is condition type
    def check_related_conditions(self, obj, cache=None):
        """ This check will return OK if all related objects that passes
            filter condition also passes check condition.

            Same as filter out all related objects that passes
            filter condition, and then check them with check conditions
        """
        # Get related field value.
        field = self.condition_rel_field_id
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
                        rel_rec, operator=filter_operator, cache=cache)):
                continue

            # check if record match 'check' conditions
            if not self.condition_rel_conditions.check(
                    rel_rec, operator=operator, cache=cache):
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
        assert date_type in ('start', 'end'), ("Date type not in (start,stop)")

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
            field = self['condition_date_diff_date_%s_field' % date_type]
            return str_to_datetime(field.ttype, obj[field.name])

    # signature check_<type> where type is condition type
    def check_date_diff(self, obj, cache=None):
        """ Check date diff

            If at least one of dates not set, than return False
        """
        date_start = self.helper_date_diff_get_date('start', obj)
        date_end = self.helper_date_diff_get_date('end', obj)

        # if at leas one field not set, fail
        if not date_start or not date_end:
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

    def helper_check_simple_field_string(self, obj_value):
        operator = self.condition_simple_field_string_operator
        is_regex = self.condition_simple_field_string_operator_regex
        is_icase = self.condition_simple_field_string_operator_icase
        reference_value = self.condition_simple_field_value_char

        # Simple operators
        if operator == 'set':
            return bool(obj_value)
        elif operator == 'not set':
            return not bool(obj_value)

        # Compute regex flags
        re_flags = re.UNICODE
        if is_icase:
            re_flags |= re.IGNORECASE

        # if not regex, do re.escape
        if not is_regex and operator in ('=', '!='):
            reference_value = u'^%s$' % re.escape(reference_value)
        elif not is_regex and operator == 'contains':
            reference_value = re.escape(
                reference_value)

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
    def check_simple_field(self, obj, cache=None):
        """ Check value of simple field of object
        """
        field = self.condition_simple_field_field_id
        value = obj[field.name]

        if field.ttype in ('integer', 'float'):
            return self.helper_check_simple_field_number(value)
        elif field.ttype == 'char':
            return self.helper_check_simple_field_string(value)
        elif field.ttype == 'boolean':
            return self.helper_check_simple_field_boolean(value)
        elif field.ttype == 'selection':
            return self.helper_check_simple_field_selection(value)
        raise NotImplementedError()

    # signature check_<type> where type is condition type
    def check_related_field(self, obj, cache=None):
        operator = self.condition_related_field_operator
        field = self.condition_related_field_field_id
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

    def _check(self, obj, cache=None):
        """ Checks one condition for a specific object
        """
        self.ensure_one()
        cache_key = (self.id, self.model_id.model, obj.id)

        # check cache
        if self.enable_caching and cache is not None and cache_key in cache:
            return cache[cache_key]

        # calculate condition
        try:
            res = getattr(self, 'check_%s' % self.type)(obj, cache=cache)
        except:
            msg = _("Error caught while evaluating condition %s[%d]"
                    "") % (self.name, self.id,)
            _logger.error(msg, exc_info=True)
            raise

        # Invert resut if required
        res = (not res) if self.invert else res

        # set cache
        if self.enable_caching and cache is not None:
            cache[cache_key] = res

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
    def check(self, obj, operator='and', cache=None):
        """ Checks if specified conditions satisfied

            :param obj: browse_record of object to be checked with conditions
            :param operator: how to join conditions. one of ('and', 'or'),
                             default: 'and'
        """
        assert operator in ('and', 'or'), "Operator must be in ('and', 'or')"

        if not obj:
            raise UserError(_("Cannot check conditions for empty recordset"))

        cache = {} if cache is None else cache

        ctx = self._prepare_object_context(obj)

        if not self:
            # if there are no conditions, assume check is ok
            return True

        # Do actual condition processing
        for cond in self:
            res = cond.with_context(ctx)._check(obj, cache=cache)
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
