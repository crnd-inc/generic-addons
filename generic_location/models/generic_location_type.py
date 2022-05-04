from odoo import models, fields, api


class GenericLocationType(models.Model):
    _name = 'generic.location.type'

    _inherit = [
        'mail.thread',
        'generic.mixin.name_with_code',
    ]
    _description = 'Location Type'

    name = fields.Char(copy=False)
    code = fields.Char(copy=False)
    active = fields.Boolean(default=True, index=True)

    # Locations
    location_ids = fields.One2many(
        'generic.location', 'type_id', 'Locations', readonly=True, copy=False)
    location_count = fields.Integer(
        'All Locations', compute='_compute_location_count', readonly=True)

    _sql_constraints = [
        ('name_uniq',
         'UNIQUE (name)',
         'Name must be unique.'),
        ('code_uniq',
         'UNIQUE (code)',
         'Code must be unique.'),
    ]

    @api.depends('location_ids')
    def _compute_location_count(self):
        for record in self:
            record.location_count = len(record.location_ids)
