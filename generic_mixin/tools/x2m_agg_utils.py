def read_counts_for(records, related_model, search_field, value_field):
    """ Read counts of if records in *related_model* for *records*,
        searching via *search_field* equal to *value_field*

        :param records: recordset with records to compute counts for
        :param str related_model: name of the related model to search for
            related records in.
        :param str search_field: name of field in related model,
            that will be used to search for related records
        :param str value_field: name of field in *records* model,
            that will be used as value for search field.
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
        data = records.env[related_model].sudo().read_group([
            (search_field, 'in', records.mapped(value_field))
        ], [search_field], [search_field])
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
