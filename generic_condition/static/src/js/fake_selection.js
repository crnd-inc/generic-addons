odoo.define('web.widgets.fake_selection_widget', function (require) {
"use strict";

/// Modify basic model with extra methods to fetch special data
var BasicModel = require('web.BasicModel');
BasicModel.include({
    _fetchSpecialFakeSelection: function (record, fieldName, fieldInfo) {
        var def;
        def = this._fetchFakeSelection(record, fieldName, fieldInfo.selection_field);
        return $.when(def);
    },
    _fetchFakeSelection: function (record, fieldName, selection_field_name) {
        var self = this;
        var def;

        var selection_field = record._changes && record._changes[selection_field_name] || record.data[selection_field_name];
        var selection_field_data = self.localData[selection_field];

        if (selection_field) {
            def = self._rpc({
                model: 'ir.model.fields',
                method: 'read',
                args: [[selection_field_data.res_id], ['name', 'model']],
                context: record.getContext({fieldName: fieldName}),
            }).then(function (result) {
                if (result.length == 1)
                    var model = result[0].model;
                    var model_field_name = result[0].name;
                    return self._rpc({
                        model: model,
                        method: 'fields_get',
                        args: [[model_field_name], ['selection']],
                        context: record.getContext({fieldName: fieldName}),
                    }).then(function (result) {
                        return result[model_field_name].selection;
                    });
            });
        }
        return $.when(def);
    },
});

// This widget allows to render selection for other field
// It is useful in case, when we have one many2one('ir.model.fields') field
// and want to display selection for selected field.
var FieldSelection = require('web.relational_fields').FieldSelection;
var FieldFakeSelection = FieldSelection.extend({

    //resetOnAnyFieldChange: true,
    template: 'FieldSelection',
    specialData: "_fetchSpecialFakeSelection",
    supportedFieldTypes: ['selection'],

    _formatValue: function (value) {
        var val = _.find(this.values, function (option) {
            return option[0] === value;
        });
        if (!val) {
            // If value not in selection, just show it
            return value;
        }
        value = val[1];
        return value;
    },

    _setValues: function () {
        this.values = this.record.specialData[this.name];
        if (!this.values) {
            this.values = [];
        }
        this.values = [[false, this.attrs.placeholder || '']].concat(this.values);
    },
});

require('web.field_registry').add('fake_selection', FieldFakeSelection);

return FieldFakeSelection;
});
