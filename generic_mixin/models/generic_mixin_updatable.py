from odoo import models, fields, api

IGNORE_NOUPDATE_ON_WRITE_FIElDS = [
    'ir_model_data_ids',
    'ir_model_data_no_update',
]


class GenericMixinDataUpdatable(models.AbstractModel):
    """ Mixin to provide easy management of updatable state on datarecord,
        via adding link to corresponding record in 'ir.model.data'

        This mixin just adds two fields:
            ir_model_data_id (readonly)
            ir_model_data_no_update (editable)
            ir_model_data_xmlid (readonly)

        Also, if you want to make record 'noupdate' on any change, you
        can set '_auto_set_noupdate_on_write' model attr to True
        For example:

            class MyModel(models.Model):
                _name = 'my.model.name'
                _inherit = 'generic.mixin.data.updatable'
                _auto_set_noupdate_on_write = True
    """
    _name = 'generic.mixin.data.updatable'
    _description = 'GenericMixin: Data Updatable'

    _auto_set_noupdate_on_write = False

    ir_model_data_ids = fields.One2many(
        'ir.model.data', 'res_id',
        domain=lambda self: [('model', '=', self._name)],
        readonly=True,
        string="Data records")
    ir_model_data_id = fields.Many2one(
        'ir.model.data', readonly=True, store=False,
        compute='_compute_ir_model_data',
        string="Data record")
    ir_model_data_no_update = fields.Boolean(
        compute='_compute_ir_model_data',
        inverse='_inverse_ir_model_data_no_update',
        search='_search_ir_model_data_no_update',
        readonly=False,
        string='Non Updatable',
        help="Indicates whether this record will be updated "
             "with module update or not. If set to True, the record "
             "will not be overriden on module update, if set to False, then"
             "record will be overridden by module update")
    ir_model_data_xmlid = fields.Char(
        compute='_compute_ir_model_data',
        # search='_search_ir_model_data_xmlid',
        readonly=True,
        string='XML ID',
        help="XML ID for this record.")

    @api.depends('ir_model_data_ids', 'ir_model_data_ids.noupdate',
                 'ir_model_data_ids.name', 'ir_model_data_ids.module')
    def _compute_ir_model_data(self):
        # Assume that there is only one xmlid per record
        ir_model_data = self.sudo().env['ir.model.data'].search([
            ('model', '=', self._name),
            ('res_id', 'in', self.ids),
        ])
        ir_model_data_map = {
            m.res_id: m for m in ir_model_data
        }
        for record in self:
            data_rec = ir_model_data_map.get(
                record.id,
                self.sudo().env['ir.model.data'].browse()
            )

            record.ir_model_data_id = data_rec
            if data_rec:
                record.ir_model_data_no_update = data_rec.noupdate
                record.ir_model_data_xmlid = data_rec.complete_name
            else:
                record.ir_model_data_no_update = True
                record.ir_model_data_xmlid = False

    def _inverse_ir_model_data_no_update(self):
        for record in self:
            if record.ir_model_data_id:
                record.ir_model_data_id.noupdate = (
                    record.ir_model_data_no_update)

    def _search_ir_model_data_no_update(self, operator, value):
        return [('ir_model_data_ids.noupdate', operator, value)]

    def write(self, vals):
        res = super(GenericMixinDataUpdatable, self).write(vals)

        if not self._auto_set_noupdate_on_write:
            return res
        if self.env.context.get('install_mode'):
            return res

        # Set noupdate for changed records
        if set(vals) - set(IGNORE_NOUPDATE_ON_WRITE_FIElDS):
            self.sudo().mapped('ir_model_data_ids').write({'noupdate': True})

        return res
