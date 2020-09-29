import logging
import collections

from odoo import models, fields, api, exceptions, _
from odoo.osv import expression

_logger = logging.getLogger(__name__)


def ensure_code_or_name(code, name):
    if not (bool(code) or bool(name)):
        raise AssertionError(
            "'code' or 'name' must not be None! (code=%s;name=%s)"
            "" % (code, name))


class GenericTag(models.Model):
    _name = "generic.tag"
    _inherit = ['generic.tag.model.mixin']
    _description = "Generic Tag"
    _access_log = False
    _rec_name = 'complete_name'
    _order = 'category_sequence, category_name, sequence, complete_name'

    category_id = fields.Many2one(
        'generic.tag.category', 'Category',
        index=True, ondelete='restrict')
    name = fields.Char(required=True, translate=True, index=True)
    code = fields.Char(
        index=True, help="May be used for special "
                         "tags which have programmed bechavior")
    sequence = fields.Integer(index=True, default=5)
    comment = fields.Text(help="Describe what this tag means")
    complete_name = fields.Char(
        compute="_compute_complete_name",
        store=True, readonly=True,
        help="Full name of tag (including category name)")
    category_sequence = fields.Integer(
        related='category_id.sequence',
        string="Category priority",
        store=True, index=True, readonly=True)
    category_name = fields.Char(
        related='category_id.name', store=True, index=True,
        string="Name of Category")
    objects_count = fields.Integer(
        string="Objects", compute="_compute_objects_count",
        store=False, readonly=True, tracking=True,
        help="How many objects contains this tag")
    group_ids = fields.Many2many('res.groups', string='Groups')
    color = fields.Integer()
    active = fields.Boolean(default=True, index=True)

    _sql_constraints = [
        ('name_uniq',
         'unique(model_id, category_id, name)',
         'Name of tag must be unique for category'),
        ('code_uniq',
         'unique(model_id, code)',
         'Code of tag must be unique'),
    ]

    @api.depends()
    def _compute_objects_count(self):
        for tag in self:
            if not tag.id:
                tag.objects_count = 0
                continue

            try:
                TagModel = self.env[tag.model_id.model]
            except KeyError:
                tag.objects_count = 0
            else:
                tag.objects_count = TagModel.search_count(
                    [('tag_ids.id', '=', tag.id)])

    @api.depends('category_id.name', 'name')
    def _compute_complete_name(self):
        for tag in self:
            if tag.category_id:
                tag.complete_name = "%s / %s" % (
                    tag.category_id.name, tag.name)
            else:
                tag.complete_name = tag.name

    @api.constrains('category_id', 'model_id')
    def _check_category_model(self):
        for tag in self:
            if tag.category_id and tag.model_id != tag.category_id.model_id:
                raise exceptions.ValidationError(_(
                    u"Category must be bound to same model as tag"))

    def name_get(self):
        return [(t.id, t.complete_name) for t in self]

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if not args:
            args = []
        if name:
            domain = [
                [('name', operator, name)],
                [('code', operator, name)],
                [('complete_name', operator, name)]
            ]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = expression.AND(domain)
            else:
                domain = expression.OR(domain)

            domain = expression.AND([domain, args])
            tags = self.search(domain, limit=limit)
        else:
            tags = self.search(args, limit=limit)

        return tags.name_get()

    @api.model
    @api.returns('self')
    def get_tags(self, model, code=None, name=None):
        """ Search for tags by model, code, name
        """
        ensure_code_or_name(code, name)
        tag_domain = [('model_id.model', '=', model)]
        if code is not None:
            tag_domain.append(('code', '=', code))
        if name is not None:
            tag_domain.append(('name', '=', name))
        return self.search(tag_domain)

    def action_show_objects(self):
        self.ensure_one()
        return {
            'name': _('Objects related to tag %s') % self.name,
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
    _description = "Generic Tag Mixin"

    @api.constrains('tag_ids')
    def _check_tags_xor(self):
        for record in self:
            categ_counter = collections.defaultdict(
                self.env['generic.tag'].browse)
            for tag in record.tag_ids:
                if tag.category_id.check_xor:
                    categ_counter[tag.category_id] |= tag

            bad_tags = []
            for category, tags in categ_counter.items():
                if len(tags) > 1:
                    bad_tags.append(
                        (category, tags)
                    )
            if bad_tags:
                msg_detail = ', '.join(
                    ('[%s - %s]' % (cat.name, ', '.join(tags.mapped('name')))
                     for cat, tags in bad_tags)
                )
                raise exceptions.ValidationError(
                    _("Following (category - tags) pairs, "
                      "break category XOR restriction:\n%s"
                      "") % msg_detail)

    def _search_no_tag_id(self, operator, value):
        with_tags = self.search([('tag_ids', operator, value)])
        return [('id', 'not in', with_tags.mapped('id'))]

    def _search_tag_id(self, operator, value):
        return [('tag_ids', operator, value)]

    def _compute_search_tag(self):
        for rec in self:
            rec.search_tag_id = False
            rec.search_no_tag_id = False

    tag_ids = fields.Many2many(
        'generic.tag', string="Tags",
        domain=lambda self: [('model_id.model', '=', self._name)])

    # Search capabilities
    search_tag_id = fields.Many2one(
        'generic.tag', string='Tag', compute='_compute_search_tag',
        search='_search_tag_id', store=False, readonly=True,
        domain=lambda self: [('model_id.model', '=', self._name)],
        help="Find all records that contain this tag")
    search_no_tag_id = fields.Many2one(
        'generic.tag', string='No tag', compute='_compute_search_tag',
        search='_search_no_tag_id', store=False, readonly=True,
        domain=lambda self: [('model_id.model', '=', self._name)],
        help="Find all records that have no this tag")

    def add_tag(self, code=None, name=None, create=False):
        """ Adds tag new tag to object.

            @param code: tag.code field to search for
            @param name: tag.name field to search for
            @param create: if True then create tag if not found
        """
        tags = self.env['generic.tag'].get_tags(
            self._name, code=code, name=name)

        if not tags and create:
            model = self.env['generic.tag.model'].search(
                [('model', '=', self._name)])[0]
            tags = self.env['generic.tag'].create({
                'name': name,
                'code': code,
                'model_id': model.id,
            })

        if tags:
            self.write({'tag_ids': [(4, t.id) for t in tags]})

    def remove_tag(self, code=None, name=None):
        """ Removes tags specified by code/name

            @param code: tag.code field to search for
            @param name: tag.name field to search for
        """
        tags = self.env['generic.tag'].get_tags(
            self._name, code=code, name=name)

        if tags:
            self.write({'tag_ids': [(3, t.id) for t in tags]})

    def check_tag(self, code=None, name=None):
        """ Check if self have tag with specified code / name
        """
        ensure_code_or_name(code, name)
        tag_domain = [('id', 'in', self.ids)]
        if code is not None:
            tag_domain.append(('tag_ids.code', '=', code))
        if name is not None:
            tag_domain.append(('tag_ids.name', '=', name))

        count = self.search_count(tag_domain)
        return bool(count == len(self))

    def check_tag_category(self, code=None, name=None):
        """ Checks if self have tag with specified
            category code and/or category name
        """
        ensure_code_or_name(code, name)
        categ_domain = [('id', 'in', self.ids)]
        if code is not None:
            categ_domain.append(('tag_ids.category_id.code', '=', code))
        if name is not None:
            categ_domain.append(('tag_ids.category_id.name', '=', name))

        count = self.search_count(categ_domain)
        return bool(count == len(self))
