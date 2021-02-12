import re
import logging
import traceback

import datetime
import dateutil
import pytz
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, exceptions, _
from odoo.tools.safe_eval import safe_eval, wrap_module

from ..utils import str_to_datetime
from ..debug_logger import DebugLogger

# dateutil submodules are lazy so need to import them for them to "exist"

_logger = logging.getLogger(__name__)


class GenericCondition(models.Model):
    _name = "generic.condition"
    _inherit = [
        'mail.thread',
        'generic.mixin.get.action',
    ]
    _order = "sequence, name"
    _description = 'Generic Condition'
    _rec_name = 'name'

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

    @api.constrains('type', 'model_id', 'condition_condition_id')
    def _constrain_condition_condition_id(self):
        for record in self:
            if record.type != 'condition':
                continue
            if record.condition_condition_id.model_id != record.model_id:
                raise exceptions.ValidationError(_(
                    "Incorrect Conditon field set for condition: "
                    "%(condition)s [%(condition_id)s]"
                ) % {
                    'condition': record.display_name,
                    'condition_id': record.id,
                })

    @api.constrains('type', 'model_id', 'condition_filter_id')
    def _constrain_condition_filter_id(self):
        for record in self:
            if record.type != 'filter':
                continue
            if record.condition_filter_id.model_id != record.model_id.model:
                raise exceptions.ValidationError(_(
                    "Incorrect Filter field set for condition: "
                    "%(condition)s [%(condition_id)s]"
                ) % {
                    'condition': record.display_name,
                    'condition_id': record.id,
                })

    @api.constrains('type', 'model_id', 'condition_condition_ids')
    def _constrain_condition_group(self):
        for record in self:
            if record.type != 'condition_group':
                continue
            for c in record.condition_condition_ids:
                if c.model_id != record.model_id:
                    raise exceptions.ValidationError(_(
                        "Incorrect Condition (condition group) selected!\n"
                        "Base condition: %(base_cond)s [%(base_cond_id)s]\n"
                        "Condition with wrong model: %(cond)s [%(cond_id)s]"
                    ) % {
                        'base_cond': record.display_name,
                        'base_cond_id': record.id,
                        'cond': c.display_name,
                        'cond_id': c.id,
                    })

    @api.constrains('type', 'model_id', 'condition_rel_field_id')
    def _constrain_condition_rel_field_id(self):
        for cond in self:
            if cond.type != 'related_conditions':
                continue
            rel_field_id = cond.condition_rel_field_id
            if rel_field_id:
                rel_field_model_id = cond.condition_rel_field_id.model_id
                if rel_field_model_id != cond.model_id:
                    raise exceptions.ValidationError(
                        _('Wrong Related Field / Based on combination'))

    color = fields.Integer()
    name = fields.Char(
        required=True, index=True, translate=True, tracking=True)
    type = fields.Selection(
        [('eval', 'Expression'),
         ('filter', 'Filter'),
         ('condition', 'Condition'),
         ('related_conditions', 'Related conditions'),
         ('date_diff', 'Date difference'),
         ('condition_group', 'Condition group'),
         ('simple_field', 'Simple field'),
         ('related_field', 'Related field'),
         ('current_user', 'Current user'),
         ('monetary_field', 'Monetary field')], default='filter', index=True,
        required=True, tracking=True)
    model_id = fields.Many2one(
        'ir.model', 'Based on model', required=True, index=True,
        ondelete='cascade',
        help="Choose model to apply condition to")
    based_on = fields.Char(
        related='model_id.model', readonly=True, index=True, store=True,
        related_sudo=True, tracking=True)
    sequence = fields.Integer(
        index=True, default=10, tracking=True,
        help="Conditions with smaller value in this field "
             "will be checked first")
    active = fields.Boolean(
        index=True, default=True, tracking=True)
    invert = fields.Boolean(
        'Invert (Not)', tracking=True,
        help="Invert condition result.")
    with_sudo = fields.Boolean(
        default=False, tracking=True,
        help="Run this condition as superuser.")
    enable_caching = fields.Boolean(
        default=True, tracking=True,
        help='If set, then condition result for a specific object will be '
             'cached during one condition chain call. '
             'This may speed up condition processing.')
    description = fields.Text(translate=True)

    # Condition type 'eval' params
    condition_eval = fields.Char(
        'Condition (eval)', required=False, tracking=True,
        help="Python expression. 'obj' are present in context.")

    # Condition type 'filter' params
    condition_filter_id = fields.Many2one(
        'ir.filters', string='Condition (filter)', auto_join=True,
        ondelete='restrict', tracking=True,
        help="User filter to be applied by this condition.")

    # Condition type 'condition' params
    condition_condition_id = fields.Many2one(
        'generic.condition', 'Condition (condition)',
        ondelete='restrict', tracking=True, auto_join=True,
        help='Link to another condition. Usualy used to get '
             'inversed condition')

    # Condition type 'condition_group' params
    condition_condition_ids = fields.Many2many(
        'generic.condition',
        'generic_condition__condition_group__rel',
        'parent_condition_id', 'sub_condition_id',
        string='Condition (condition group)',
        tracking=True, auto_join=True,
        help='Check set of other conditions')
    condition_condition_ids_operator = fields.Selection(
        '_get_selection_condition_condition_ids_operator', default='and',
        string='Condition (condition group): operator',
        tracking=True)

    # Condition type 'current_user' params
    condition_user_check_type = fields.Selection(
        [('field', 'Field'),
         ('one_of', 'One of'),
         ('checks', 'Checks')],
        string="Check Type", default='field', tracking=True)
    condition_user_user_field_id = fields.Many2one(
        'ir.model.fields', string='User Field',
        ondelete='cascade', tracking=True,
        domain=[('ttype', 'in', ('many2one', 'one2many', 'many2many')),
                ('relation', '=', 'res.users')],
        help='Field in object being checked, that points to user.')
    condition_user_one_of_user_ids = fields.Many2many(
        'res.users', 'generic_conditon__current_user__one_of__user_rel',
        string='Users', tracking=True)
    condition_user_checks_condition_ids = fields.Many2many(
        'generic.condition',
        'generic_condition__current_user__checks__condition_ids',
        'parent_condition_id', 'child_condition_id',
        domain=[('based_on', '=', 'res.users')],
        string='Conditions', tracking=True)

    # Condition type 'related_conditions' params
    condition_rel_field_id = fields.Many2one(
        'ir.model.fields', string='Related Field',
        ondelete='cascade', auto_join=True, tracking=True,
        domain=[('ttype', 'in', ('many2one', 'one2many', 'many2many'))])
    condition_rel_field_id_model_id = fields.Many2one(
        comodel_name='ir.model',
        compute='_compute_condition_rel_field_id_model_id',
        compute_sudo=True,
        string='Related field: model', readonly=True, store=False)
    condition_rel_record_operator = fields.Selection(
        [('match', 'Match'),
         ('contains', 'Contains')],
        string='Related record operator', default='match',
        help='Choose way related record will be checked:\n'
             '- Match: return True if all filtered records match condition.\n'
             '- Contains: return True if at least one of filtered records '
             'match \'check\' conditions',
        tracking=True)
    condition_rel_filter_conditions = fields.Many2many(
        'generic.condition', 'generic_condition_filter_conds',
        'parent_id', 'child_id', ondelete='restrict', auto_join=True,
        string='Related filter conditions', tracking=True,
        help="Used together with Related Field. "
             "These conditions are used to filter related items that "
             "will be checked by 'Related check conditions'. "
             "If this conditions evaluates to False for some object, "
             "that this object will not be checked")
    condition_rel_filter_conditions_operator = fields.Selection(
        '_get_selection_condition_condition_ids_operator', default='and',
        string='Related filter conditions operator',
        tracking=True)
    condition_rel_conditions = fields.Many2many(
        'generic.condition', 'generic_condition_check_conds',
        'parent_id', 'child_id', ondelete='restrict', auto_join=True,
        string='Related check conditions', tracking=True,
        help="Used together with Related Field. "
             "These conditions will be used to check objects "
             "that passed filter conditions. "
             "And result of these related conditions will be used as result")
    condition_rel_conditions_operator = fields.Selection(
        '_get_selection_condition_condition_ids_operator', default='and',
        string='Related check conditions operator',
        tracking=True)

    # Date difference fields: start date
    condition_date_diff_date_start_type = fields.Selection(
        '_get_selection_date_diff_date_type',
        string='Date start type', default='now', tracking=True)
    condition_date_diff_date_start_field = fields.Many2one(
        'ir.model.fields', 'Date start field', ondelete='cascade',
        domain=[('ttype', 'in', ('date', 'datetime'))],
        tracking=True)
    condition_date_diff_date_start_date = fields.Date(
        'Date start', default=fields.Date.today, tracking=True)
    condition_date_diff_date_start_datetime = fields.Datetime(
        'Date start', default=fields.Datetime.now, tracking=True)

    # Date difference fields: end date
    condition_date_diff_date_end_type = fields.Selection(
        '_get_selection_date_diff_date_type',
        string='Date end type', default='now', tracking=True)
    condition_date_diff_date_end_field = fields.Many2one(
        'ir.model.fields', 'Date end field', ondelete='cascade',
        domain=[('ttype', 'in', ('date', 'datetime'))],
        tracking=True)
    condition_date_diff_date_end_date = fields.Date(
        'Date end', default=fields.Date.today, tracking=True)
    condition_date_diff_date_end_datetime = fields.Datetime(
        'Date end', default=fields.Datetime.now, tracking=True)

    # Date difference fields: check rules
    condition_date_diff_operator = fields.Selection(
        [('=', '='),
         ('>', '>'),
         ('<', '<'),
         ('>=', '>='),
         ('<=', '<='),
         ('!=', '!=')],
        string='Date diff operator', tracking=True)
    condition_date_diff_uom = fields.Selection(
        [('minutes', 'Minutes'),
         ('hours', 'Hours'),
         ('days', 'Days'),
         ('weeks', 'Weeks'),
         ('months', 'Months'),
         ('years', 'Years')],
        string='Date diff UoM', tracking=True,
        help='Choose Unit of Measurement for date diff here')
    condition_date_diff_value = fields.Integer('Date diff value')
    condition_date_diff_absolute = fields.Boolean(
        'Absolute', default=False,
        help='If checked, then absolute date difference will be checked. '
             '(date difference will be positive always)',
        tracking=True)

    # Simple field conditions
    condition_simple_field_field_id = fields.Many2one(
        'ir.model.fields', 'Check field', ondelete='cascade',
        domain=[('ttype', 'in', ('boolean', 'char', 'text',
                                 'html', 'float',
                                 'integer', 'selection'))],
        tracking=True)
    condition_simple_field_type = fields.Selection(
        related='condition_simple_field_field_id.ttype', related_sudo=True,
        string='Field type', readonly=True, tracking=True)
    condition_simple_field_value_boolean = fields.Selection(
        [('true', 'True'), ('false', 'False')], 'Value',
        tracking=True)
    condition_simple_field_value_char = fields.Char(
        'Value', tracking=True)
    condition_simple_field_value_float = fields.Float(
        'Value', tracking=True)
    condition_simple_field_value_integer = fields.Integer(
        'Value', tracking=True)
    condition_simple_field_value_selection = fields.Char(
        'Value', tracking=True)
    condition_simple_field_selection_operator = fields.Selection(
        [('=', '='),
         ('!=', '!='),
         ('set', 'Set'),
         ('not set', 'Not set')],
        string='Operator', tracking=True)
    condition_simple_field_number_operator = fields.Selection(
        [('=', '='),
         ('>', '>'),
         ('<', '<'),
         ('>=', '>='),
         ('<=', '<='),
         ('!=', '!=')], string='Operator', tracking=True)
    condition_simple_field_string_operator = fields.Selection(
        [('=', '='),
         ('!=', '!='),
         ('set', 'Set'),
         ('not set', 'Not set'),
         ('contains', 'Contains')],
        string='Operator', tracking=True)
    condition_simple_field_string_operator_html = fields.Selection(
        [('set', 'Set'),
         ('not set', 'Not set'),
         ('contains', 'Contains')],
        string='Operator', tracking=True)
    condition_simple_field_string_operator_icase = fields.Boolean(
        'Case insensitive', tracking=True)
    condition_simple_field_string_operator_regex = fields.Boolean(
        'Regular expression', tracking=True)

    # Related field conditions
    condition_related_field_field_id = fields.Many2one(
        'ir.model.fields', 'Check field', ondelete='cascade',
        domain=[('ttype', 'in', ('many2one', 'many2many'))])
    condition_related_field_model = fields.Char(
        string='Related Model', related_sudo=True, readonly=True,
        related='condition_related_field_field_id.relation',
        help="Technical name of related field's model",
        tracking=True)
    condition_related_field_operator = fields.Selection(
        [('set', 'Set'),
         ('not set', 'Not set'),
         ('contains', 'Contains')],
        string='Operator', tracking=True)
    condition_related_field_value_id = fields.Integer(
        'Value', tracking=True)

    # Monetary field conditions
    # Value monetary fields
    condition_monetary_field_id = fields.Many2one(
        'ir.model.fields', 'Field', ondelete='cascade',
        domain=[('ttype', '=', 'monetary')], tracking=True)
    condition_monetary_currency_field_id = fields.Many2one(
        'ir.model.fields', 'Currency', ondelete='cascade',
        domain=[('ttype', '=', 'many2one'),
                ('relation', '=', 'res.currency')],
        help="Field with currency for field being checked",
        tracking=True)

    # Monetary fields: check rules
    condition_monetary_operator = fields.Selection(
        [('=', '='),
         ('>', '>'),
         ('<', '<'),
         ('>=', '>='),
         ('<=', '<='),
         ('!=', '!=')], string='Operator', tracking=True)
    condition_monetary_value = fields.Monetary(
        'Value', currency_field='condition_monetary_value_currency_id',
        tracking=True)
    condition_monetary_value_currency_id = fields.Many2one(
        'res.currency', 'Currency', ondelete='restrict',
        tracking=True)
    # Monetary fields: currency date
    condition_monetary_curency_date_type = fields.Selection(
        [('now', 'Current date'),
         ('field', 'Field'),
         ('date', 'Date')],
        string='Type', default='now', tracking=True)
    condition_monetary_curency_date_field_id = fields.Many2one(
        'ir.model.fields', 'Field', ondelete='cascade',
        domain=[('ttype', 'in', ('date', 'datetime'))],
        tracking=True)
    condition_monetary_curency_date_date = fields.Date(
        'Date', default=fields.Date.today, tracking=True)

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
            else:
                cond.condition_rel_field_id_model_id = False

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
            obj_name = "%s [id:%s] (%s)" % (
                self.sudo().model_id.model, obj.id,
                obj.sudo().name_get()[0][1])
            _logger.error(
                "Error was cauht when checking condition %s on document %s. "
                "condition expression:\n%s\n", condition_name, obj_name,
                self.condition_eval, exc_info=True)
            raise exceptions.ValidationError(_(
                "Checking condition %(cond)s on document %(doc)s "
                "caused error. Notify administrator to fix it.\n"
                "\n---\n%(error_msg)s"
            ) % {
                'cond': condition_name,
                'doc': obj_name,
                'error_msg': traceback.format_exc(),
            })
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
                if self.condition_rel_record_operator == 'match':
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
        if date_source == 'date':
            date = self['condition_date_diff_date_%s_date' % date_type]
            return str_to_datetime('date', date)
        if date_source == 'datetime':
            date = self['condition_date_diff_date_%s_datetime' % date_type]
            return str_to_datetime('datetime', date)
        if date_source == 'field':
            field_name = 'condition_date_diff_date_%s_field' % date_type
            field = self.sudo()[field_name]
            return str_to_datetime(field.ttype, obj[field.name])

    # signature check_<type> where type is condition type
    def check_current_user(self, obj, cache=None, debug_log=None):
        if self.condition_user_check_type == 'field':
            field = self.sudo().condition_user_user_field_id
            if obj[field.name] and self.env.user in obj[field.name]:
                return True
        elif self.condition_user_check_type == 'one_of':
            if self.env.user in self.sudo().condition_user_one_of_user_ids:
                return True
        elif self.condition_user_check_type == 'checks':
            if self.condition_user_checks_condition_ids.check(self.env.user):
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
            'minutes': lambda d1, d2, dt: dt.minutes,
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
        if operator == '!=':
            return uom_map[uom](date_end, date_start, delta) != value
        if operator in operator_map:
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
        if operator == 'not set':
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
        if obj_value and operator == '!=':
            return not bool(
                re.match(
                    reference_value,
                    obj_value,
                    re_flags))
        if not obj_value and operator == '!=':
            # False != reference_value
            return True
        if obj_value and operator == 'contains':
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
        if operator == 'not set':
            return not bool(obj_value)
        if operator == '=':
            return obj_value == reference_value
        if operator == '!=':
            return obj_value != reference_value

    # signature check_<type> where type is condition type
    def check_simple_field(self, obj, cache=None, debug_log=None):
        """ Check value of simple field of object
        """
        field = self.sudo().condition_simple_field_field_id
        value = obj[field.name]

        if field.ttype in ('integer', 'float'):
            return self.helper_check_simple_field_number(value)
        if field.ttype in ('char', 'text', 'html'):
            return self.helper_check_simple_field_string(value)
        if field.ttype == 'boolean':
            return self.helper_check_simple_field_boolean(value)
        if field.ttype == 'selection':
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
        if operator == 'not set':
            return not bool(obj_value)
        if obj_value and operator == 'contains':
            reference_value_id = self.condition_related_field_value_id
            return reference_value_id in obj_value.ids
        return False

    def helper_check_monetary_field_date(self, obj):
        # Compute accounting date
        if self.condition_monetary_curency_date_type == 'date':
            return self.condition_monetary_curency_date_date
        if self.condition_monetary_curency_date_type == 'field':
            currency_date_field = (
                self.condition_monetary_curency_date_field_id.sudo())
            return obj[currency_date_field.name]
        return fields.Datetime.now()

    # signature check_<type> where type is condition type
    def check_monetary_field(self, obj, cache=None, debug_log=None):
        # pylint: disable=too-many-locals
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
        company = (
            self.env['res.company'].browse(self.env.context['company_id'])
            if self.env.context.get('company_id')
            else self.env.company
        )
        test_value = obj_val_currency._convert(
            obj_val, reference_currency, company, date)

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
            raise exceptions.UserError(_(
                "Generic conditions misconfigured!\n"
                "object's model and condition's model does not match:\n"
                "\tcondition: %(condition)s [%(condition_id)d]"
                "\tobject: %(object)s [%(object_id)d]"
                "\tobject's model: %(object_model)s\n"
                "\tcondition's model: %(condition_model)s\n"
            ) % {
                'condition': self.display_name,
                'condition_id': self.id,
                'object': obj.display_name,
                'object_id': obj.id,
                'object_model': obj._name,
                'condition_model': self.based_on,
            })

        self._debug_log(debug_log, obj, "Computing...")

        # Is sudo condition?
        condition = self
        if self.with_sudo:
            condition = self.sudo()
            obj = obj.sudo()
            self._debug_log(debug_log, obj, "Using sudo")

        # generate cache_key
        cache_key = (condition.id, obj.id)

        # check cache
        if (condition.enable_caching and
                cache is not None and
                cache_key in cache):
            self._debug_log(
                debug_log, obj, "Using cached result: %s" % cache[cache_key])
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
            _logger.error(
                "Error caught while evaluating condition %s[%d]",
                condition.name, condition.id, exc_info=True)
            raise

        # Invert result if required
        res = (not res) if condition.invert else res

        # set cache
        if condition.enable_caching and cache is not None:
            cache[cache_key] = res

        self._debug_log(debug_log, obj, "Computed result: %s" % res)
        return res

    @api.model
    def _prepare_object_context(self, obj):
        """ Prepare context to check conditions for object object

            This method may be used as hook, by other modules
            to fill evaluation context with extra values
        """
        mods = ['parser', 'relativedelta', 'rrule', 'tz']
        for mod in mods:
            __import__('dateutil.%s' % mod)
        _datetime = wrap_module(
            __import__('datetime'),
            ['date', 'datetime', 'time', 'timedelta', 'timezone',
             'tzinfo', 'MAXYEAR', 'MINYEAR'])
        _dateutil = wrap_module(dateutil, {
            mod: getattr(dateutil, mod).__all__
            for mod in mods
        })
        _relativedelta = dateutil.relativedelta.relativedelta
        _time = wrap_module(
            __import__('time'), ['time', 'strptime', 'strftime'])
        _timezone = pytz.timezone

        return {
            'obj': obj,
            'record': obj,
            'env': self.env,
            'model': self.env[obj._name],
            'uid': self._uid,
            'user': self.env.user,
            'time': _time,
            'datetime': _datetime,
            'dateutil': _dateutil,
            'relativedelta': _relativedelta,
            'timezone': _timezone,
        }

    def check(self, obj, operator='and', cache=None, debug_log=None):
        """ Checks if specified conditions satisfied

            :param obj: browse_record of object to be checked with conditions
            :param operator: how to join conditions. one of ('and', 'or'),
                             default: 'and'
        """
        if operator not in ('and', 'or'):
            raise AssertionError("Operator must be in ('and', 'or')")

        if not obj:
            raise exceptions.UserError(
                _("Cannot check conditions for empty recordset"))

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
            if operator == 'or' and res:
                # if operator is or, then return ok on first successful check
                return True

        if operator == 'and':
            # there are no failed checks, so return ok
            return True
        if operator == 'or':
            # there are no successful check, so all checks are failed, return
            # fail
            return False

    def action_show_test_wizard(self):
        self.ensure_one()
        return self.get_action_by_xmlid(
            'generic_condition.action_generic_condition_test_wizard_view',
            context=dict(
                self.env.context,
                default_condition_id=self.id),
        )
