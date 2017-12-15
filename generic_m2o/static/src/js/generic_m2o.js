odoo.define('web.widgets.generic_m2o_widget', function (require) {
"use strict";

var core = require('web.core');
var many2one = core.form_widget_registry.get('many2one');


var FieldGenericM2O = many2one.extend( {
    template: "FieldMany2One",

    init: function(field_manager, node) {
        this._super(field_manager, node);
        this.can_create = false;
        this.can_write = false;
        this.model_field = this.node.attrs.model_field;
    },
    update_field_relation: function() {
        this.field.relation = this.field_manager.get_field_value(
            this.model_field);
    },
    get_search_result: function(search_val) {
        this.update_field_relation();
        return this._super(search_val);
    },

    render_value: function(no_recurse) {
        this.update_field_relation();
        return this._super(no_recurse);
    },
});

core.form_widget_registry.add('generic_m2o', FieldGenericM2O);

});
