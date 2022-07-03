from odoo.osv import expression


def read_counts_for(records, related_model, search_field, value_field,
                    domain=None, sudo=False):
    """ Read counts of if records in *related_model* for *records*,
        searching via *search_field* equal to *value_field*

        :param records: recordset with records to compute counts for
        :param str related_model: name of the related model to search for
            related records in.
        :param str search_field: name of field in related model,
            that will be used to search for related records
        :param str value_field: name of field in *records* model,
            that will be used as value for search field.
        :param list domain: Additional domain to apply to records found
        :param bool sudo: Use sudo to search records. Default: False
        :return dict: Mapping of values of search fields, and counts of recods.

        Typical usecase would be to compute counts for one2many fields.

        class MyModel(models.Model):
            _name = 'my.model'

            other_ids = fields.One2many('other.model', 'my_model_id')
            other_count = fields.Integer(
                compute='_compute_other_count')

            @api.depends()
            def _compute_other_count(self):
                mapped_data = read_counts_for(
                    records=self,
                    related_model='other.model',
                    search_field='my_model_id',
                    value_field='id')
                for record in self:
                    record.other_count = mapped_data.get(record.id, 0)
    """
    if records.ids:
        check_values = (
            records.ids
            if value_field == 'id'
            else records.mapped(value_field)
        )
        RelatedModel = records.env[related_model]
        if sudo:
            RelatedModel = RelatedModel.sudo()

        search_domain = [(search_field, 'in', check_values)]
        if domain:
            search_domain = expression.AND([search_domain, domain])
        data = RelatedModel.read_group(
            search_domain, [search_field], [search_field])
        mapped_data = {}
        for m in data:
            key = m[search_field]
            if isinstance(key, (tuple, list)):
                # For many2one fields
                key = key[0]
            mapped_data[key] = m['%s_count' % search_field]
    else:
        # For case, if record is not written in db
        mapped_data = dict()
    return mapped_data


def read_counts_for_o2m(records, field_name, domain=None, sudo=False):
    """ Read counds for specified one2many field.

        :param records: recordset with records to compute counts for
        :param str field_name: name of one2many field to compute counts for
        :param list domain: Additional domain to apply to records found
        :param bool sudo: Use sudo to search records. Default: False
        :return dict: Mapping of values of search fields, and counts of recods.

        Typical usecase would be to compute counts for one2many fields.

        class MyModel(models.Model):
            _name = 'my.model'

            other_ids = fields.One2many('other.model', 'my_model_id')
            other_count = fields.Integer(
                compute='_compute_other_count')

            @api.depends()
            def _compute_other_count(self):
                mapped_data = read_counts_for_o2m(
                    records=self,
                    field_name='other_ids')
                for record in self:
                    record.other_count = mapped_data.get(record.id, 0)
    """
    field = records._fields[field_name]
    if field.type != 'one2many':
        raise ValueError(
            "Incorrect type of field %s. Expected: %s. Got: %s"
            "" % (field_name, 'one2many', field.type))

    return read_counts_for(
        records=records,
        related_model=field.comodel_name,
        search_field=field.inverse_name,
        value_field='id',
        domain=domain,
        sudo=sudo,
    )
