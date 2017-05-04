# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.tools import (DEFAULT_SERVER_DATETIME_FORMAT,
                           DEFAULT_SERVER_DATE_FORMAT)
from openerp.exceptions import ValidationError, UserError
import datetime
from dateutil.relativedelta import relativedelta

import traceback

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
            # ('tags', _('Tags')),
            ('condition', _('Condition')),
            ('related_conditions', _('Related conditions')),
            ('date_diff', _('Date difference')),
            ('condition_group', _('Condition group')),
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

    def _get_selection_condition_condition_ids_operator(self):
        return [
            ('or',  _('OR')),
            ('and',  _('AND')),
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

    color = fields.Integer('Color')
    name = fields.Char('Name', required=True, index=True)
    type = fields.Selection(
        '_get_selection_type', default='filter',
        string='Type', index=True, required=True)
    model_id = fields.Many2one(
        'ir.model', 'Based on model', required=True, index=True)
    based_on = fields.Char(
        related='model_id.model', readonly=True, index=True, store=True,
        string='Based on')
    sequence = fields.Integer('Sequence', index=True, default=10)
    active = fields.Boolean('Active', index=True, default=True)
    invert = fields.Boolean('Invert (Not)')
    enable_caching = fields.Boolean(
        'Enable caching', default=True,
        help='If set, then condition result for a specific object will be '
             'cached during one condition chain call. '
             'This may speed_up condition processing.')
    condition_eval = fields.Char(
        'Condition (eval)', required=False, track_visibility='onchange',
        help="Python expression. 'obj' are present in context.")
    # condition_tag_ids = fields.Many2many(
    #    'res.tag', 'generic_condition_tags_rel',
    #    'cond_id', 'tag_id', string='Condition (tags)', auto_join=True,
    #    help='There must be at least one of specified tag present in repair')
    condition_filter_id = fields.Many2one(
        'ir.filters', string='Condition (filter)', auto_join=True,
        ondelete='restrict', track_visibility='onchange',
        help="If present, this condition must be satisfied to apply "
             "this rule.")
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
        help='Links to another conditions')
    condition_condition_ids_operator = fields.Selection(
        '_get_selection_condition_condition_ids_operator', default='and',
        string='Group operator', track_visibility='onchange')

    # Related conditions
    condition_rel_field_id = fields.Many2one(
        'ir.model.fields', 'Related Field',
        ondelete='restrict', auto_join=True,
        domain=[('ttype', 'in', ('many2one', 'one2many', 'many2many'))])
    condition_rel_field_id_model_id = fields.Many2one(
        'ir.model', compute='_compute_condition_rel_field_id_model_id',
        string='Related field relation', readonly=True)
    condition_rel_record_operator = fields.Selection(
        '_get_selection_condition_rel_record_operator',
        'Related record operator', default='match',
        help='Choose way related record will be chacked:\n'
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
        string='Group filter conditions operator', track_visibility='onchange')
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
        string='Group related conditions operator',
        track_visibility='onchange')

    # Data difference fields
    condition_date_diff_date_field_start = fields.Many2one(
        'ir.model.fields', 'Date start field', ondelete='restrict',
        domain=[('ttype', 'in', ('date', 'datetime'))])
    condition_date_diff_date_field_end = fields.Many2one(
        'ir.model.fields', 'Date end field', ondelete='restrict',
        domain=[('ttype', 'in', ('date', 'datetime'))])
    condition_date_diff_operator = fields.Selection(
        '_get_selection_date_diff_operator',
        string='Date diff operator')
    condition_date_diff_uom = fields.Selection(
        '_get_selection_date_diff_uom',
        string='Date diff UoM')
    condition_date_diff_value = fields.Integer('Date diff value')

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
        domain = [('id', '=', obj.id)] + eval(filter_obj.domain)

        ctx = self.env.context.copy()
        ctx.update(eval(filter_obj.context, ctx))
        return bool(Model.with_context(ctx).search(domain, count=True))

    # signature check_<type> where type is condition type
    def check_eval(self, obj, cache=None):
        try:
            res = bool(eval(self.condition_eval, dict(self.env.context)))
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
    # def check_tags(self, obj, cache=None):
    #    condition_tags = [t.id for t in condition.condition_tag_ids]
    #    return any((1
    #                for tag in obj.tag_ids
    #                if tag.id in condition_tags))

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

    # signature check_<type> where type is condition type
    def check_date_diff(self, obj, cache=None):
        """ Check date diff

            If at least one of dates not set, than return False
        """
        def to_datetime(field, value):
            if field.ttype == 'datetime':
                return datetime.datetime.strptime(
                    value, DEFAULT_SERVER_DATETIME_FORMAT)
            elif field.ttype == 'date':
                return datetime.datetime.strptime(
                    value, DEFAULT_SERVER_DATE_FORMAT)

        date_start_field = self.condition_date_diff_date_field_start
        date_end_field = self.condition_date_diff_date_field_end

        # get data from object
        date_start = obj[date_start_field.name]
        date_end = obj[date_end_field.name]

        # if at leas one field not set, fail
        if not date_start or not date_end:
            return False

        # Convert field data to datetime
        date_start = to_datetime(date_start_field, date_start)
        date_end = to_datetime(date_end_field, date_end)

        # if dates not in correct order then swap them
        # TODO: check box 'absolute diff'
        if date_end < date_start:
            date_start, date_end = date_end, date_start

        # delta betwen two dates
        delta = relativedelta(date_end, date_start)

        uom = self.condition_date_diff_uom
        value = self.condition_date_diff_value
        operator = self.condition_date_diff_operator

        # used for operators '==' and '!='
        uom_map = {
            'hours': lambda d1, d2, dt: (d1 - d2).total_seconds() / 60.0 / 60.0,  # noqa
            'days': lambda d1, d2, dt: (d1 - d2).days,
            'weeks': lambda d1, d2, dt: uom_map['days'](d1, d2, dt) / 7.0,
            'months': lambda d1, d2, dt: dt.months + dt.years * 12,
            'years': lambda d1, d2, dt: dt.years,
        }

        if operator == '=':
            return uom_map[uom](date_end, date_start, delta) == value
        elif operator == '!=':
            return uom_map[uom](date_end, date_start, delta) != value
        elif operator == '>':
            # EX: date_end - date_start > 2 years
            #     equal to
            #     date_start + 2 year < date_end
            return date_start + relativedelta(**{uom: value}) < date_end
        elif operator == '>=':
            # EX: date_end - date_start >= 2 years
            #     equal to
            #     date_start + 2 year <= date_end
            return date_start + relativedelta(**{uom: value}) <= date_end
        elif operator == '<':
            # EX: date_end - date_start < 2 years
            #     equal to
            #     date_start + 2 year > date_end
            return date_start + relativedelta(**{uom: value}) > date_end
        elif operator == '<=':
            # EX: date_end - date_start <= 2 years
            #     equal to
            #     date_start + 2 year >= date_end
            return date_start + relativedelta(**{uom: value}) >= date_end
        else:
            raise ValidationError(
                _("Unsupported operator '%s' for condition '%s'"
                  "") % (operator, self.name))

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
        return {'obj': obj}

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
