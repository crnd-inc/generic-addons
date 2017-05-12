from openerp import models, fields, api
from openerp.tools.translate import _

import logging
_logger = logging.getLogger(__name__)


class ResTagModel(models.Model):
    _name = "res.tag.model"
    _description = "Contains list of models available for tagging"

    _access_log = False

    @api.multi
    #@api.depends('model_id')
    def _compute_tags_count(self):
        for model in self:
            model.tags_count = self.env['res.tag'].search_count([('model_id', '=', model.id)])

    
    name = fields.Char("Name", size=64, required=True, select=True, translate=True)
    model = fields.Char("Model", size=32, required=True, select=True)
    tags_count = fields.Integer(string="Tags", compute="_compute_tags_count", store=False, readonly=True,
                                      track_visibility='always',
                                      help="How many tags related to this model exists")
    

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
            'res_model': 'res.tag',
            'type': 'ir.actions.act_window',
            'context': ctx,
            'domain': [('model_id.id', '=', model.id)],
        }


class ResTagModelMixin(models.AbstractModel):
    _name = "res.tag.model.mixin"
    _description = "Mixin to add res.tag.model relation"

    def _get_default_model_id(self, cr, uid, context=None):
        """ Try to get default model from context and find approriate res.tag.model record ID
        """
        if context is None:
            context = {}

        default_model = context.get('default_model', False)
        if default_model:
            tag_model_obj = self.pool.get('res.tag.model')
            model_ids = tag_model_obj.search(cr, uid, [('model', '=', default_model)], limit=1, context=context)
            if model_ids:
                return model_ids[0]

        return False


    model_id = fields.Many2one("res.tag.model", "Model", required=True, ondelete='restrict',
                                    select=True, help="Specify model for which this tag is available")


    _defaults = {
        "model_id": lambda s, *a, **k: s._get_default_model_id(*a, **k),
    }


class ResTagCategory(models.Model):
    _name = 'res.tag.category'
    _inherit = ['res.tag.model.mixin']
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

        # tag_obj = self.tag_ids.category_id
        # tags_count = len(tag_obj)
        # res = {}.fromkeys(ids, 0)
        # for category_id in self.:
        #     res[category_id] = tag_obj.search(cr, uid[('category_id.id', '=', category_id)], count=1, context=context)
        # _logger.info("CREATE. RES:CREATE. RES:CREATE. RES:CREATE. RES:CREATE. RES:CREATE. RES: %s", res)
        # _logger.info("CREATE. TAGOBJ:CREATE. TAGOBJ:CREATE. TAGOBJ:CREATE. TAGOBJ: %s", tag_obj)
        # return res


        # model_id field will be added by 'res.tag.model.mixin'
    name = fields.Char("Name", size=64, required=True,
                            translate=True, select=True)
    code = fields.Char("Code", size=32, select=True,
                            help="May be used for special tags which have programming meaning")
    comment = fields.Text("Comment", help="Describe what this tag means")

    active = fields.Boolean("Active", select=True)

    tag_ids = fields.One2many("res.tag", "category_id", "Tags")

    check_xor = fields.Boolean("Check XOR", help="if set to True then enables XOR check on tags been added to object. "
                                                      "it means that only one tag from category may be added to object at time")
    tags_count = fields.Float(string="Tags", compute="_compute_tags_count", store=True, readonly=True,
                                      track_visibility='always',
                                      help="How many tags related to this catgory exists")


    _defaults = {
        "active": True,
    }

    _sql_constraints = [
        ('name_uniq', 'unique(model_id, name)', 'Name of category must be unique'),
        ('code_uniq', 'unique(model_id, code)', 'Code of category must be unique'),
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
            'res_model': 'res.tag',
            'type': 'ir.actions.act_window',
            'context': ctx,
            'domain': [('category_id.id', '=', category.id)],
        }


class ResTag(models.Model):
    _name = "res.tag"
    _inherit = ['res.tag.model.mixin']
    _description = "Tag"

    _access_log = False

    _rec_name = 'display_name'
    _order = 'display_name'

    @api.multi
    def _compute_objects_count(self):
        for tag in self:
            tag.objects_count = self.env[tag.model_id.model].search_count([('tag_ids.id', '=', tag.id)])


    @api.multi
    @api.depends('category_id', 'name')
    def _compute_display_name(self):
        for tag in self:
            if tag.category_id:
                tag.display_name = "%s / %s" % (tag.category_id.name, tag.name)
            else:
                tag.display_name = tag.name


        # res = {}.fromkeys(ids, '')
        # for tag in self.browse(cr, uid, ids, context=context):
        #     if tag.category_id:
        #         res[tag.id] = "%s / %s" % (tag.category_id.name, tag.name)
        #     else:
        #         res[tag.id] = tag.name
        # return res

    def _check_category_id(self, cr, uid, ids, context=None):
        for tag in self.browse(cr, uid, ids, context=context):
            if tag.category_id and tag.model_id != tag.category_id.model_id:
                return False
        return True

        # model_id field will be added by 'res.tag.model.mixin'
    category_id = fields.Many2one('res.tag.category', 'Category', select=True, ondelete='restrict')
    name = fields.Char("Name", size=64, required=True,
                            translate=True, select=True)
    code = fields.Char("Code", size=32, select=True,
                            help="May be used for special tags which have programming meaning")
    comment = fields.Text("Comment", help="Describe what this tag means")

    active = fields.Boolean("Active", select=True)

    display_name = fields.Char(string="Tags", compute="_compute_display_name", store=True, readonly=True,
                                      track_visibility='always',
                                      help="Full name of tag (including category name")

    # complete_name = fields.Function(lambda self, *a, **k: self._get_complete_name(*a, **k),
    #                                      string="Name", type='Char', store={
    #                                          'res.tag': (lambda s, c, u, ids, ctx=None: ids, [], 10),
    #                                          'res.tag.category': (lambda s, cr, uid, ids, context=None:
    #                                                               s.pool.get('res.tag').search(cr, uid,
    #                                                                                            [('category_id', 'in', ids)]),
    #                                                               ['name'],
    #                                                               10)
    #                                      },
    #                                      help="Full name of tag (including category name"),
    objects_count = fields.Integer(string="Tags", compute="_compute_objects_count", store=False, readonly=True,
                                      track_visibility='always',
                                      help="How many objects contains this tag")
    group_ids = fields.Many2many('res.groups', string='Groups')
    color = fields.Integer("Color")

    _defaults = {
        "active": True,
    }

    _sql_constraints = [
        ('name_uniq', 'unique(model_id, name)', 'Name of tag must be unique'),
        ('code_uniq', 'unique(model_id, code)', 'Code of tag must be unique'),
    ]

    _constraints = [
        (_check_category_id,
         "Category must be binded to same model as tag",
         ['category_id', 'model_id']),
    ]

    def get_tag_ids(self, cr, uid, model, code=None, name=None, context=None):
        """ Returns list of IDs of tags for specified model name by (code, name) pair

            @param model: string that represents model name like 'res.partner'
            @return: list of IDs of res.tag objects
        """
        assert bool(code) or bool(name), "code or name must not be None! (code=%s;name=%s)" % (code, name)
        tag_domain = [('model_id.model', '=', model)]
        if code is not None:
            tag_domain.append(('code', '=', code))
        if name is not None:
            tag_domain.append(('name', '=', name))
        return self.search(cr, uid, tag_domain, context=context)

    def action_show_objects(self, cr, uid, ids, context=None):
        assert len(ids) == 1, "Can be applied only to one tag at time"
        tag = self.browse(cr, uid, ids[0], context=context)
        return {
            'name': _('Objects related to tag %s') % tag.name,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': tag.model_id.model,
            'type': 'ir.actions.act_window',
            'context': context,
            'domain': [('tag_ids.id', '=', tag.id)],
        }


class ResTagMixin(models.AbstractModel):
    """ Mixin to be used to add tag support to any model by inheriting from it like:
            _inherit=["res.tag.mixin"]
    """
    _name = "res.tag.mixin"
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
            FROM %(table)s             AS st
            LEFT JOIN %(tag_rel)s      AS trel   ON trel.%(obj_id_field)s = st.id
            LEFT JOIN res_tag          AS rt     ON trel.%(tag_id_field)s = rt.id
            LEFT JOIN res_tag_category AS rtc    ON rt.category_id = rtc.id
            WHERE rtc.check_xor = True
                AND st.id IN (%(obj_ids)s)
            GROUP BY st.id, rtc.id
            HAVING count(rt.id) > 1
        """ % sql_params)
        if cr.rowcount > 0:
            bad_rows = cr.fetchall()
            # Prepare messsage to display in what objects / categories
            # validation error occured
            tag_category_obj = self.pool.get('res.tag.category')
            message = _("There are more that one tag for tag category for folowing pairs object - category pairs:\n")
            obj_ids = []
            categ_ids = []
            for obj_id, categ_id in bad_rows:
                message += "\t(%%(obj_%d)s: %%(cat_%d)s\n" % (obj_id, categ_id)
                obj_ids.append(obj_id)
                categ_ids.append(categ_id)
            data = {}
            data.update({'obj_%d' % oid: name for oid, name in self.name_get(cr, uid, obj_ids, context=context)})
            data.update({'cat_%d' % cid: name for cid, name in tag_category_obj.name_get(cr, uid, categ_ids, context=context)})
            raise orm.except_orm(_("ValidateError"), message % data)

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
    #             with_tag_ids = self.search(cr, uid, [('tag_ids.id', op, right)], context=context)
    #         elif isinstance(right, basestring):
    #             u = '|' if op != '!=' else '&'
    #             with_tag_ids = self.search(cr, uid, [u, ('tag_ids.complete_name', op, right),
    #                                                     ('tag_ids.code', op, right)], context=context)
    #         elif isinstance(right, (list, tuple)) and op in ('in', 'not in'):
    #             with_tag_ids = self.search(cr, uid, [('tag_ids', op, right)], context=context)
    #         else:
    #             continue

    #         res.append(('id', 'not in', with_tag_ids))

    #     return res

    tag_ids = fields.Many2many('res.tag', string="Tags", select=True,
                                    domain=lambda self: [('model_id.model', '=', self._name)])
    # no_tag_id = fields.Function(lambda self, cr, uid, ids, fnames, args, context=None: {}.fromkeys(ids, False),
    #                                  method=True, store=False,
    #                                  fnct_search=lambda s, *a, **ka: s._search_no_tag_id(*a, **ka),
    #                                  string="No Tag", obj='res.tag', type='Many2one', readonly=True,
    #                                  domain=lambda self: [('model_id.model', '=', self._name)])

    _constraints = [
        (lambda s, *a, **k: s._check_tags_xor(*a, **k),
         "More than one tag of category with 'check_xor' enabled, present in object",
         ['tag_ids']),
    ]

    def add_tag(self, cr, uid, ids, code=None, name=None, create=False, context=None):
        """ Adds tag new tag to object.

            @param code: tag.code field to search for
            @param name: tag.name field to search for
            @param create: if True then create tag if not found
            @return: True if at least one tag was added
        """
        tag_obj = self.pool.get('res.tag')
        tag_ids = tag_obj.get_tag_ids(cr, uid, self._name, code=code, name=name, context=context)
        if not tag_ids and create:
            model_id = self.pool.get('res.tag.model').search(cr, uid, [('model', '=', self._name)])[0]
            tag_ids = [tag_obj.create(cr, uid, {'name': name, 'code': code, 'model_id': model_id}, context=context)]

        if tag_ids:
            self.write(cr, uid, ids, {'tag_ids': [(4, tid) for tid in tag_ids]}, context=context)

        return bool(tag_ids)

    def remove_tag(self, cr, uid, ids, code=None, name=None, context=None):
        """ Removes tags specified by code/name from specified cargoes

            @param code: tag.code field to search for
            @param name: tag.name field to search for
            @return: True if specified tags were found (even if they are not present in records passed

            Note: return value is not suitable for checking if something was removed
        """
        tag_obj = self.pool.get('res.tag')
        tag_ids = tag_obj.get_tag_ids(cr, uid, self._name, code=code, name=name, context=context)

        if tag_ids:
            self.write(cr, uid, ids, {'tag_ids': [(3, tid) for tid in tag_ids]}, context=context)

        return bool(tag_ids)

    def check_tag(self, cr, uid, ids, code=None, name=None, context=None):
        """ Checks if all of supplied objects have tag with specified code and/or name
            Return True if all object ids has specified tags
        """
        assert bool(code is not None) or bool(name is not None), "code or name must not be None"
        tag_domain = [('id', 'in', ids)]
        if code is not None:
            tag_domain.append(('tag_ids.code', '=', code))
        if name is not None:
            tag_domain.append(('tag_ids.name', '=', name))

        count = self.search(cr, uid, tag_domain, count=1)
        return bool(count == len(ids))

    def check_tag_category(self, cr, uid, ids, code=None, name=None, context=None):
        """ Checks if all of supplied objects have tag with specified category code and/or category name
            Return True if all object ids has specified tag category
        """
        assert bool(code is not None) or bool(name is not None), "code or name must not be None"
        tag_domain = [('id', 'in', ids)]
        if code is not None:
            tag_domain.append(('tag_ids.category_id.code', '=', code))
        if name is not None:
            tag_domain.append(('tag_ids.category_id.name', '=', name))

        count = self.search(cr, uid, tag_domain, count=1)
        return bool(count == len(ids))
