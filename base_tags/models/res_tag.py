from openerp.osv import orm, fields
from openerp.tools.translate import _


class ResTagModel(orm.Model):
    _name = "res.tag.model"
    _description = "Contains list of models available for tagging"

    _access_log = False
    _columns = {
        "name": fields.char("Name", size=64, required=True, select=True, translate=True),
        "model": fields.char("Model", size=32, required=True, select=True),
    }

    _sql_constraints = [
        ('model_uniq', 'unique(model)', 'Model field must be unique'),
    ]
ResTagModel()


class ResTag(orm.Model):
    _name = "res.tag"
    _description = "Can be used to tag objects"

    _access_log = False

    def _get_default_model_id(self, cr, uid, context=None):
        if context is None:
            context = {}

        default_model = context.get('default_model', False)
        if default_model:
            tag_model_obj = self.pool.get('res.tag.model')
            model_ids = tag_model_obj.search(cr, uid, [('model', '=', default_model)], limit=1, context=context)
            if model_ids:
                return model_ids[0]

        return False

    def _get_objects_count(self, cr, uid, ids, field_name, arg, context=None):
        res = {}.fromkeys(ids, 0)
        for tag in self.browse(cr, uid, ids, context=context):
            rel_obj = self.pool.get(tag.model_id.model)
            res[tag.id] = rel_obj.search(cr, uid, [('tag_ids.id', '=', tag.id)], count=1, context=context)
        return res

    _columns = {
        "model_id": fields.many2one("res.tag.model", "Model", required=True,
                                    select=True, help="Specify model for which this tag is available"),
        "name": fields.char("Name", size=64, required=True,
                            translate=True, select=True),
        "code": fields.char("Code", size=32, select=True,
                            help="May be used for special tags which have programming meaning"),
        "comment": fields.text("Comment", help="Describe what this tag means"),

        "active": fields.boolean("Active", select=True),

        "objects_count": fields.function(lambda self, *a, **k: self._get_objects_count(*a, **k),
                                         string="Objects", type='integer', store=False,
                                         help="How many objects contains this tag"),
        "group_ids": fields.many2many('res.groups', string='Groups'),
    }

    _defaults = {
        "model_id": _get_default_model_id,
        "active": True,
    }

    _sql_constraints = [
        ('name_uniq', 'unique(model_id, name)', 'Name of tag must be unique'),
        ('code_uniq', 'unique(model_id, code)', 'Code of tag must be unique'),
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

ResTag()


class ResTagMixin(orm.AbstractModel):
    """ Mixin to be used to add tag support to any model by inheriting from it like:
            _inherit=["res.tag.mixin"]
    """
    _name = "res.tag.mixin"
    _description = "Adds tag_ids field to object"

    _columns = {
        'tag_ids': fields.many2many('res.tag', string="Tags", select=True,
                                    domain=lambda self: [('model_id.model', '=', self._name)]),
    }

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
            @return: True if atleast one tag was added
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
        assert bool(code is None) or bool(name is None), "code or name must not be None"
        tag_domain = [('id', 'in', ids)]
        if code is not None:
            tag_domain.append(('tag_ids.code', '=', code))
        if name is not None:
            tag_domain.append(('tag_ids.name', '=', name))

        count = self.search(cr, uid, tag_domain, count=1)
        return bool(count == len(ids))

ResTagMixin()
