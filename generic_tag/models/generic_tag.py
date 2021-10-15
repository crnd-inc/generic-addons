import logging

from odoo import models, fields, api, exceptions, _
from odoo.osv import expression

from ..utils import ensure_code_or_name

_logger = logging.getLogger(__name__)


class GenericTag(models.Model):
    _name = "generic.tag"
    _inherit = [
        'generic.tag.model.mixin'
    ]
    _description = "Generic Tag"
    _access_log = False
    _rec_name = 'name'
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
        if self.env.context.get('_use_standart_name_get_', False):
            return super(GenericTag, self).name_get()
        return [(t.id, t.complete_name) for t in self]

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
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
