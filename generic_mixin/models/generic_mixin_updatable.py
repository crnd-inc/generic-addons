from odoo import models, fields, api


class GenericMixinDataUpdatable(models.AbstractModel):
    """ Mixin to provide easy management of updatable state on datarecord,
        via adding link to corresponding record in 'ir.model.data'

        This mixin just adds two fields:
            ir_model_data_id (readonly)
            ir_model_data_no_update (editable)
    """
    _name = 'generic.mixin.data.updatable'
    _description = 'GenericMixin: Data Updatable'

    ir_model_data_ids = fields.One2many(
        'ir.model.data', 'res_id',
        domain=lambda self: [('model', '=', self._name)],
        readonly=True)
    ir_model_data_id = fields.Many2one(
        'ir.model.data', readonly=True, store=False,
        compute='_compute_ir_model_data')
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
        readonly=False,
        string='XML ID',
        help="XML ID for this record.")

    @api.depends('ir_model_data_ids', 'ir_model_data_ids.noupdate',
                 'ir_model_data_ids.name', 'ir_model_data_ids.module')
    def _compute_ir_model_data(self):
        # Assume that there is only one xmlid per record
        ir_model_data = self.env['ir.model.data'].search([
            ('model', '=', self._name),
            ('res_id', 'in', self.ids),
        ])
        ir_model_data_map = {
            m.res_id: m for m in ir_model_data
        }
        for record in self:
            data_rec = ir_model_data_map.get(
                record.id,
                self.env['ir.model.data'].browse()
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
            record.ir_model_data_id.noupdate = record.ir_model_data_no_update

    def _search_ir_model_data_no_update(self, operator, value):
        return [('ir_model_data_ids.noupdate', operator, value)]
