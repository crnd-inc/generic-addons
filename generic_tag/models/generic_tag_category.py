from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class GenericTagCategory(models.Model):
    _name = 'generic.tag.category'
    _inherit = ['generic.tag.model.mixin']
    _description = "Generic Tag Category"
    _order = 'sequence'
    _access_log = False

    @api.depends('tag_ids')
    def _compute_tags_count(self):
        for line in self:
            line.tags_count = len(line.tag_ids)

    # model_id field will be added by 'generic.tag.model.mixin'
    name = fields.Char(required=True, translate=True, index=True)
    code = fields.Char(
        index=True, help="May be used for special "
                         "tags which have programmed bechavior")
    comment = fields.Text(help="Describe what this tag category is for")
    active = fields.Boolean(index=True, default=True)
    tag_ids = fields.One2many(
        "generic.tag", "category_id", "Tags", readonly=True)
    check_xor = fields.Boolean(
        "Check XOR",
        help="if set to True then only one tag from this category "
             "may be present on a single object. "
             "On attempt to add second tag from this category to object, "
             "error will be raised")
    tags_count = fields.Float(
        compute="_compute_tags_count", store=True,
        readonly=True, tracking=True,
        help="How many tags related to this catgory")
    color = fields.Integer()
    sequence = fields.Integer(index=True, default=5)

    _sql_constraints = [
        ('name_uniq', 'unique(model_id, name)',
         'Name of category must be unique'),
        ('code_uniq', 'unique(model_id, code)',
         'Code of category must be unique'),
    ]

    @api.constrains('model_id')
    def _check_model_id(self):
        for category in self:
            tag_model = category.tag_ids.mapped('model_id')
            if tag_model and (len(tag_model) != 1 or
                              tag_model != category.model_id):
                raise ValidationError(_(
                    u"Model must be same as one used in related tags"))

    def action_show_tags(self):
        self.ensure_one()
        ctx = dict(self.env.context,
                   default_model_id=self.model_id.id,
                   default_category_id=self.id)
        return {
            'name': _('Tags related to category %s') % self.name,
            'view_mode': 'tree,form',
            'res_model': 'generic.tag',
            'type': 'ir.actions.act_window',
            'context': ctx,
            'domain': [('category_id.id', '=', self.id)],
        }
