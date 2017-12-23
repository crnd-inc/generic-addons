odoo.define('web.widgets.generic_m2o_widget', function (require) {
"use strict";

var core = require('web.core');
var field_registry = require('web.field_registry');
var field_utils = require('web.field_utils');
var FieldMany2One = require('web.relational_fields').FieldMany2One;


/// Modify basic model with extra methods to fetch special data
var BasicModel = require('web.BasicModel');
BasicModel.include({
    _fetchSpecialGenericM2O: function (record, fieldName, fieldInfo) {
        var def;
        var field = record.fields[fieldName];
        if (field.type === 'integer') {
            def = this._fetchGenericM2O(record, fieldName, fieldInfo.model_field);
        }
        return $.when(def);
    },
    _fetchGenericM2O: function (record, fieldName, model_field) {
        var self = this;
        var def;

        var field = record.fields[fieldName];
        var model = record._changes && record._changes[model_field] || record.data[model_field];
        var res = record._changes && record._changes[fieldName] || record.data[fieldName];

        if (model && model !== 'False' && res) {
            if (res.id === undefined)
                var resID = res;
            else
                var resID = res.id;

            if (resID) {
                def = self._rpc({
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
                        if (result.length >= 1)
                            return self._makeDataPoint({
                                data: {
                                    id: result[0][0],
                                    display_name: result[0][1],
                                },
                                modelName: model,
                                parentID: record.id,
                            });
                    });
                });
            }
        }
        return $.when(def);
    },
});


// Define new GenericM2O field widget
var FieldGenericM2O = FieldMany2One.extend( {
    resetOnAnyFieldChange: true,
    supportedFieldTypes: ['integer'],
    specialData: "_fetchSpecialGenericM2O",
    template: "FieldMany2One",

    init: function() {
        this._super.apply(this, arguments);

        // Configure widget options
        this.can_create = false;
        this.can_write = false;
        this.nodeOptions.quick_create = false;

        this.value = this.record.specialData[this.name];
        this.m2o_value = this._formatValue(this.value);

        this.model_field = this.attrs.model_field;

        // needs to be copied as it is an unmutable object
        this.field = _.extend({}, this.field);

        this._update_field_relation();
    },
    _update_field_relation: function () {
        if (this.record._changes)
            this.field.relation = this.record._changes[this.model_field];
        else
            this.field.relation = this.record.data[this.model_field];
        return this.field.relation;
    },
    _formatValue: function (value) {
        if (value == 0)
            return '';

        value = this.record.specialData[this.name];
        return value && value.data && value.data.display_name || '';
    },
    _parseValue: function (value) {
        if ($.isNumeric(value) && Number.isInteger(value))
            return value;
        return field_utils.parse['integer'](value, this.field, this.parseOptions);
    },
    _setValue: function (value, options) {
        value = value.id;
        return this._super(value, options);
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


field_registry.add('generic_m2o', FieldGenericM2O);

return FieldGenericM2O;
});
