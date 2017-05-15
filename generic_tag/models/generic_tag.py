# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)


class GenericTagModel(models.Model):
    _name = "generic.tag.model"
    _description = "Contains list of models available for tagging"

    _access_log = False

    @api.multi
    # @api.depends('model_id')
    def _compute_tags_count(self):
        for model in self:
            model.tags_count = self.env['generic.tag'].search_count(
                [('model_id', '=', model.id)])

    name = fields.Char(size=64, required=True, translate=True)
    model = fields.Char(size=32, required=True)
    tags_count = fields.Integer(string="Tags", compute="_compute_tags_count",
                                store=False, readonly=True,
                                track_visibility='always',
                                help="How many tags related to this model"
                                     "exists")

    _sql_constraints = [
        ('model_uniq', 'unique(model)', 'Model field must be unique'),
    ]

    def action_show_tags(self, cr, uid, ids, context=None):
        assert len(ids) == 1, "Can be applied only to one tag at time"
        model = self.browse(cr, uid, ids[0], context=context)
        ctx = {} if context is None else context.copy()
        ctx['default_model_id'] = model.id
        return {
            'name': _('Tags related to model %s') % model.name,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'generic_model': 'generic.tag',
            'type': 'ir.actions.act_window',
            'context': ctx,
            'domain': [('model_id.id', '=', model.id)],
        }


class GenericTagModelMixin(models.AbstractModel):
    _name = "generic.tag.model.mixin"
    _description = "Mixin to add generic.tag.model relation"

    @api.model
    def _get_default_model_id(self):
        """ Try to get default model from context and find
            approriate generic.tag.model record ID
        """

        default_model = self.env.context.get('default_model', False)
        tag_model_obj = self.env['generic.tag.model']
        if default_model:

            return tag_model_obj.search(
                [('model', '=', default_model)], limit=1)

        return tag_model_obj.browse()

    model_id = fields.Many2one(
        "generic.tag.model", "Model", required=True, ondelete='restrict',
        default=_get_default_model_id,
        help="Specify model for which this tag is available")


class GenericTagCategory(models.Model):
    _name = 'generic.tag.category'
    _inherit = ['generic.tag.model.mixin']
    _description = "Category to group tags in"

    _access_log = False

    def _check_model_id(self, cr, uid, ids, context=None):
        for category in self.browse(cr, uid, ids, context=context):
            for tag in category.tag_ids:
                if tag.model_id != category.model_id:
                    return False
        return True

    @api.multi
    @api.depends('tag_ids')
    def _compute_tags_count(self):
        for line in self:
            line.tags_count = len(line.tag_ids)

        # model_id field will be added by 'generic.tag.model.mixin'
    name = fields.Char(size=64, required=True, translate=True)
    code = fields.Char(
        size=32, help="May be used for special"
        "tags which have programming meaning")
    comment = fields.Text(help="Describe what this tag means")

    active = fields.Boolean(string="Active", default=True)

    tag_ids = fields.One2many("generic.tag", "category_id", "Tags")

    check_xor = fields.Boolean(
        "Check XOR", help="if set to True then enables"
        "XOR check on tags been added to object. "
        "it means that only one tag from category "
        "may be added to object at time")
    tags_count = fields.Float(
        string="Tags", compute="_compute_tags_count", store=True,
        readonly=True, track_visibility='always',
        help="How many tags related to this catgory exists")
    _sql_constraints = [
        ('name_uniq', 'unique(model_id, name)',
         'Name of category must be unique'),
        ('code_uniq', 'unique(model_id, code)',
         'Code of category must be unique'),
    ]

    _constraints = [
        (_check_model_id,
         "Model must be same as one used in related tags",
         ['model_id']),
    ]

    def action_show_tags(self, cr, uid, ids, context=None):
        assert len(ids) == 1, "Can be applied only to one category at time"
        category = self.browse(cr, uid, ids[0], context=context)
        ctx = {} if context is None else context.copy()
        ctx['default_category_id'] = category.id
        ctx['default_model_id'] = category.model_id.id
        return {
            'name': _('Tags related to category %s') % category.name,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'generic_model': 'generic.tag',
            'type': 'ir.actions.act_window',
            'context': ctx,
            'domain': [('category_id.id', '=', category.id)],
        }


class GenericTag(models.Model):
    _name = "generic.tag"
    _inherit = ['generic.tag.model.mixin']
    _description = "Tag"

    _access_log = False

    _rec_name = 'display_name'
    _order = 'display_name'

    @api.multi
    def _compute_objects_count(self):
        for tag in self:
            tag.objects_count = self.env[tag.model_id.model].search_count(
                                        [('tag_ids.id', '=', tag.id)])

    @api.multi
    @api.depends('category_id', 'name')
    def _compute_display_name(self):
        for tag in self:
            if tag.category_id:
                tag.display_name = "%s / %s" % (tag.category_id.name, tag.name)
            else:
                tag.display_name = tag.name

    @api.constrains('category_id', 'model_id')
    def _check_category_id(self):
        for tag in self.browse():
            if tag.category_id and tag.model_id != tag.category_id.model_id:
                raise ValidationError(
                    u"Category must be binded to same model as tag")

        # model_id field will be added by 'generic.tag.model.mixin'
    category_id = fields.Many2one(
        'generic.tag.category', 'Category', ondelete='restrict')
    name = fields.Char(size=64, required=True, translate=True)
    code = fields.Char(
        size=32, help="May be used for special"
        "tags which have programming meaning")
    comment = fields.Text(help="Describe what this tag means")

    active = fields.Boolean(string="Active", default=True)

    display_name = fields.Char(
        string="Tags", compute="_compute_display_name",
        store=True, readonly=True, track_visibility='always',
        help="Full name of tag (including category name")

    objects_count = fields.Integer(
        string="Tags", compute="_compute_objects_count",
        store=False, readonly=True, track_visibility='always',
        help="How many objects contains this tag")
    group_ids = fields.Many2many('res.groups', string='Groups')
    color = fields.Integer()

    _sql_constraints = [
        ('name_uniq', 'unique(model_id, name)', 'Name of tag must be unique'),
        ('code_uniq', 'unique(model_id, code)', 'Code of tag must be unique'),
    ]

    @api.model
    @api.returns('self')
    def get_tag_ids(self, model, code=None, name=None):
        """ Returns list of IDs of tags for specified model name by (code, name) pair

            @param model: string that represents model name like 'res.partner'
            @return: list of IDs of res.tag objects
        """
        assert bool(code) or bool(name), (
            "code or name must not be None! (code=%s;name=%s)"
            "" % (code, name))
        tag_domain = [('model_id.model', '=', model)]
        if code is not None:
            tag_domain.append(('code', '=', code))
        if name is not None:
            tag_domain.append(('name', '=', name))
        return self.search(tag_domain)

    @api.multi
    def action_show_objects(self):
        self.ensure_one()
        return {
            'name': _('Objects related to tag %s') % self.name,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': self.model_id.model,
            'type': 'ir.actions.act_window',
            'context': self.env.context,
            'domain': [('tag_ids.id', '=', self.id)],
        }


class GenericTagMixin(models.AbstractModel):
    """ Mixin to be used to add tag support to any model
        by inheriting from it like:
            _inherit=["generic.tag.mixin"]
    """
    _name = "generic.tag.mixin"
    _description = "Adds tag_ids field to object"

    # Mail thread integration field. if set to True then tag add / remove
    # actions will be displayed in chatter
    _track_tags = False

    def _check_tags_xor(self, cr, uid, ids, context=None):
        tbl, col1, col2 = self._columns['tag_ids']._sql_names(self)
        sql_params = {
            'table': self._table,
            'tag_rel': tbl,
            'obj_id_field': col1,
            'tag_id_field': col2,
            'obj_ids': ','.join((str(i) for i in ids)),
        }
        cr.execute("""
            SELECT st.id, rtc.id
            FROM %(table)s                 AS st
            LEFT JOIN %(tag_rel)s          AS trel   ON trel.%(obj_id_field)s = st.id
            LEFT JOIN generic_tag          AS rt     ON trel.%(tag_id_field)s = rt.id
            LEFT JOIN generic_tag_category AS rtc    ON rt.category_id = rtc.id
            WHERE rtc.check_xor = True
                AND st.id IN (%(obj_ids)s)
            GROUP BY st.id, rtc.id
            HAVING count(rt.id) > 1
        """ % sql_params)   # noqa
        if cr.rowcount > 0:
            bad_rows = cr.fetchall()
            # Prepare messsage to display in what objects / categories
            # validation error occured
            tag_category_obj = self.pool.get('generic.tag.category')
            message = _("There are more that one tag for tag category for"
                        "folowing pairs object - category pairs:\n")
            obj_ids = []
            categ_ids = []
            for obj_id, categ_id in bad_rows:
                message += "\t(%%(obj_%d)s: %%(cat_%d)s\n" % (obj_id, categ_id)
                obj_ids.append(obj_id)
                categ_ids.append(categ_id)
            data = {}
            data.update({'obj_%d' % oid: name for oid, name in self.name_get(
                cr, uid, obj_ids, context=context)})
            data.update({'cat_%d' % cid: name for cid,
                        name in tag_category_obj.name_get(
                            cr, uid, categ_ids, context=context)})
            raise ValidationError("ValidateError")
            # raise orm.except_orm(_("ValidateError"), message % data)

        return True

    # def _search_no_tag_id(self, cr, uid, obj, name, args, context=None):
    #     res = []
    #     for arg in args:
    #         if isinstance(arg, basestring):  # It should be operator
    #             res.append(arg)

    #         left, op, right = arg
    #         if left != 'no_tag_id':
    #             res.append(args)
    #         elif isinstance(right, (int, long)):
    #             with_tag_ids = self.search(
    #                 cr, uid, [('tag_ids.id', op, right)], context=context)
    #         elif isinstance(right, basestring):
    #             u = '|' if op != '!=' else '&'
    #             with_tag_ids = self.search(
    #                 cr, uid, [u, ('tag_ids.complete_name', op, right),
    #                 ('tag_ids.code', op, right)], context=context)
    #         elif isinstance(right, (list, tuple)) and op in ('in', 'not in'):
    #             with_tag_ids = self.search(
    #                 cr, uid, [('tag_ids', op, right)], context=context)
    #         else:
    #             continue

    #         res.append(('id', 'not in', with_tag_ids))

    #     return res

    tag_ids = fields.Many2many(
        'generic.tag', string="Tags",
        domain=lambda self: [('model_id.model', '=', self._name)])
    # no_tag_id = fields.Function(
    #     lambda self, cr, uid, ids, fnames, args,
    #     context=None: {}.fromkeys(ids, False),
    #     method=True, store=False,
    #     fnct_search=lambda s, *a, **ka: s._search_no_tag_id(*a, **ka),
    #     string="No Tag", obj='generic.tag', type='Many2one', readonly=True,
    #     domain=lambda self: [('model_id.model', '=', self._name)])

    _constraints = [
        (lambda s, *a, **k: s._check_tags_xor(*a, **k),
         "More than one tag of category with 'check_xor'"
         "enabled, present in object",
         ['tag_ids']),
    ]

    @api.multi
    def add_tag(self, code=None, name=None, create=False):
        """ Adds tag new tag to object.

            @param code: tag.code field to search for
            @param name: tag.name field to search for
            @param create: if True then create tag if not found
            @return: True if at least one tag was added
        """
        tag_obj = self.env['generic.tag']
        tags = tag_obj.get_tag_ids(self._name, code=code, name=name)
        if not tags and create:
            model = self.env['generic.tag.model'].search(
                [('model', '=', self._name)])[0]
            tags = tag_obj.create(
                {'name': name, 'code': code, 'model_id': model.id})

        if tags:
            self.write({'tag_ids': [(4, t.id) for t in tags]})
            return True

        return False

    @api.multi
    def remove_tag(self, code=None, name=None):
        """ Removes tags specified by code/name from specified cargoes

            @param code: tag.code field to search for
            @param name: tag.name field to search for
            @return: True if specified tags were found
             (even if they are not present in records passed

            Note: return value is not suitable for checking
             if something was removed
        """
        tag_obj = self.env['generic.tag']
        tags = tag_obj.get_tag_ids(self._name, code=code, name=name)

        if tags:
            self.write({'tag_ids': [(3, t.id) for t in tags]})

            return True

        return False

    @api.multi
    def check_tag(self, code=None, name=None):
        """ Checks if all of supplied objects have tag with specified code and/or name
            Return True if all object ids has specified tags
        """
        assert bool(code is not None) or bool(name is not None), (
            "code or name must not be None")
        tag_domain = [('id', 'in', self.ids)]
        if code is not None:
            tag_domain.append(('tag_ids.code', '=', code))
        if name is not None:
            tag_domain.append(('tag_ids.name', '=', name))

        count = self.search_count(tag_domain)
        return bool(count == len(self.ids))

    @api.multi
    def check_tag_category(self, code=None, name=None):
        """ Checks if all of supplied objects have tag with specified
            category code and/or category name
            Return True if all object ids has specified tag category
        """
        assert bool(code is not None) or bool(name is not None), (
            "code or name must not be None")
        tag_domain = [('id', 'in', self.ids)]
        if code is not None:
            tag_domain.append(('tag_ids.category_id.code', '=', code))
        if name is not None:
            tag_domain.append(('tag_ids.category_id.name', '=', name))

        count = self.search_count(tag_domain)
        return bool(count == len(self.ids))
