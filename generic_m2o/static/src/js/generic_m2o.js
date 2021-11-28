/** @odoo-module **/

import fieldRegistry from 'web.field_registry';
import fieldUtils from 'web.field_utils';
import BasicModel from 'web.BasicModel';
import { FieldMany2One } from 'web.relational_fields';

function _get_record_field (record, field_name) {
    if (record._changes && record._changes[field_name]) {
        return record._changes[field_name];
    }
    return record.data[field_name];
}

// Modify basic model with extra methods to fetch special data
BasicModel.include({
    _readUngroupedList: function (list) {
        var self = this;
        var def = this._super.apply(this, arguments);
        return def.then(function () {
            return $.when(self._fetchGenericM2OsBatched(list));
        }).then(function () {
            return list;
        });
    },
    _fetchGenericM2OsBatched: function (list) {
        var defs = [];
        var fieldNames = list.getFieldNames();
        for (var i = 0; i < fieldNames.length; i++) {
            var fieldName = fieldNames[i];
            var fieldInfo = list.fieldsInfo[list.viewType][fieldName];
            if (fieldInfo.widget === 'generic_m2o') {
                defs.push(this._fetchGenericM2OBatched(list, fieldName));
            }
        }
        return $.when.apply($, defs);
    },
    _fetchGenericM2OBatched: function (list, fieldName) {
        var self = this;
        var wlist = this._applyX2ManyOperations(list);
        var defs = [];

        var fieldInfo = wlist.fieldsInfo[wlist.viewType][fieldName];
        _.each(wlist.data, function (dataPoint) {
            var record = self.localData[dataPoint];
            defs.push(
                $.when(
                    self._fetchGenericM2O(
                        record,
                        fieldName,
                        fieldInfo.model_field)
                ).then(function (specialData) {
                    record.specialData[fieldName] = specialData;
                })
            );
        });
        return $.when.apply($, defs);
    },
    _fetchSpecialGenericM2O: function (record, fieldName, fieldInfo) {
        var field = record.fields[fieldName];
        if (field.type === 'integer' ||
                field.type === 'many2one_reference') {
            return this._fetchGenericM2O(
                record, fieldName, fieldInfo.model_field);
        }
        return $.when();
    },
    _fetchGenericM2O: function (record, fieldName, model_field) {
        var self = this;

        var model = _get_record_field(record, model_field);
        var res = _get_record_field(record, fieldName);

        if (model && model !== 'False' && res) {
            var resID = null;
            if (typeof res.id === 'undefined') {
                resID = res;
            } else {
                resID = res.id;
            }

            if (resID) {
                return self._rpc({
                    model: model,
                    method: 'exists',
                    args: [resID],
                    context: record.getContext({fieldName: fieldName}),
                }).then(function (existant_records) {
                    return self._rpc({
                        model: model,
                        method: 'name_get',
                        args: [existant_records],
                        context: record.getContext({fieldName: fieldName}),
                    }).then(function (result) {
                        if (result.length >= 1) {
                            return self._makeDataPoint({
                                data: {
                                    id: result[0][0],
                                    display_name: result[0][1],
                                },
                                modelName: model,
                                parentID: record.id,
                            });
                        }
                        return self._makeDataPoint({
                            data: {
                                id: 0,
                                display_name: undefined,
                            },
                            modelName: model,
                            parentID: record.id,
                        });
                    });
                });
            }
        }
        return $.when();
    },
});

// Define new GenericM2O field widget
var FieldGenericM2O = FieldMany2One.extend( {
    resetOnAnyFieldChange: true,
    supportedFieldTypes: ['integer', 'many2one_reference'],
    specialData: "_fetchSpecialGenericM2O",
    template: "FieldMany2One",

    init: function () {
        this._super.apply(this, arguments);

        // Configure widget options
        this.can_create = false;
        this.can_write = false;
        this.nodeOptions.quick_create = false;

        this.value = this.record.specialData[this.name];
        this.m2o_value = this._formatValue(this.value);

        this.model_field = this.attrs.model_field;

        // Needs to be copied as it is an unmutable object
        this.field = _.extend({}, this.field);

        this._update_field_relation();
    },

    _update_field_relation: function () {
        if (this.record._changes) {
            this.field.relation = this.record._changes[this.model_field];
        } else {
            this.field.relation = this.record.data[this.model_field];
        }
        return this.field.relation;
    },
    _formatValue: function (value) {
        if (value === 0) {
            return '';
        }

        var val = this.record.specialData[this.name];
        if (val && val.data && val.data.display_name) {
            return val.data.display_name;
        }
        return '';
    },
    _parseValue: function (value) {
        if ($.isNumeric(value) && Number.isInteger(value)) {
            return value;
        }
        return fieldUtils.parse.integer(
            value, this.field, this.parseOptions);
    },
    _setValue: function (value, options) {
        var val = value.id;
        return this._super(val, options);
    },
    _search: function () {
        this._update_field_relation();
        return this._super.apply(this, arguments);
    },
    reinitialize: function () {
        this._update_field_relation();
        this._super.apply(this, arguments);
    },
});

fieldRegistry.add('generic_m2o', FieldGenericM2O);

export default FieldGenericM2O;
