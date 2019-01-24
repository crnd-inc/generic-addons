odoo.define('web.widgets.fake_selection_widget', function (require) {
"use strict";

var core = require('web.core');
var Model = require('web.DataModel');

var field_selection = core.form_widget_registry.get('selection');

// This widget allows to render selection for other field
// It is useful in case, when we have one many2one('ir.model.fields') field
// and want to display selection for selected field.
var FieldFakeSelection = field_selection.extend( {
    template: 'FieldSelection',

    init: function(field_manager, node) {
        this._super(field_manager, node);
        this.selection_field = this.node.attrs.selection_field;
        this.field_manager.on(
            'field_changed:' + this.selection_field,
            this,
            function() {
                this.query_values();
            }
        );
    },

    query_values: function() {
        var self = this;

        var selection_field_id = self.field_manager.get_field_value(
            self.selection_field);

        if (!selection_field_id) {
            // skip if field not selected
            self.set("values", []);
            return;
        }

        var ModelFields = new Model('ir.model.fields', self.build_context());
        ModelFields.query(['model', 'name']).filter(
            [['id', '=', selection_field_id]]
        ).first().then(function (field){
                var field_name = field.name;
                var field_model = new Model(field.model, self.build_context());
                field_model.call(
                    "fields_get",
                    [field.name],
                    {"context": self.build_context()}
                ).then(function (field_def) {
                    var selection = field_def[field_name].selection || [];
                    var selection_values = _.reject(selection, function (v) {
                        return v[0] === false && v[1] === '';
                    });
                    var def = $.when(selection_values);
                    self.records_orderer.add(def).then(function(values) {
                        if (! _.isEqual(values, self.get("values"))) {
                            self.set("values", values);
                        }
                    });
                });
        });
    },
});

core.form_widget_registry.add('fake_selection', FieldFakeSelection);


});
