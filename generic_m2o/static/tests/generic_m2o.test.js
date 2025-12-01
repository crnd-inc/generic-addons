/** @odoo-module **/

import { expect, test } from "@odoo/hoot";
import { click, queryOne, queryAll } from "@odoo/hoot-dom";
import { animationFrame } from "@odoo/hoot-mock";
import {
    defineModels,
    fields,
    models,
    mountView,
    onRpc,
} from "@web/../tests/web_test_helpers";


class TestModel extends models.Model {
    _name = "test.model";

    name = fields.Char();
    res_model = fields.Char();
    res_id = fields.Integer();

    _records = [
        { id: 1, name: "Test Record 1", res_model: "res.partner", res_id: 1 },
        { id: 2, name: "Test Record 2", res_model: "res.partner", res_id: false },
    ];
}

class Partner extends models.Model {
    _name = "res.partner";

    name = fields.Char();

    _records = [
        { id: 1, name: "Partner 1" },
        { id: 2, name: "Partner 2" },
    ];
}

defineModels([TestModel, Partner]);


test("GenericMany2OneField renders in form view", async () => {
    onRpc("name_get", () => {
        return [[1, "Partner 1"]];
    });

    await mountView({
        type: "form",
        resModel: "test.model",
        resId: 1,
        arch: `
            <form>
                <field name="res_model" invisible="1"/>
                <field name="res_id" widget="generic_m2o" options="{'model_field': 'res_model'}"/>
            </form>
        `,
    });

    expect(".o_field_widget[name='res_id']").toHaveCount(1);
});


test("GenericMany2OneField displays linked record name", async () => {
    onRpc("name_get", () => {
        return [[1, "Partner 1"]];
    });

    await mountView({
        type: "form",
        resModel: "test.model",
        resId: 1,
        arch: `
            <form>
                <field name="res_model" invisible="1"/>
                <field name="res_id" widget="generic_m2o" options="{'model_field': 'res_model'}"/>
            </form>
        `,
    });

    await animationFrame();

    const input = queryOne(".o_field_widget[name='res_id'] input");
    expect(input).toBeTruthy();
});


test("GenericMany2OneField renders empty when no value", async () => {
    await mountView({
        type: "form",
        resModel: "test.model",
        resId: 2,
        arch: `
            <form>
                <field name="res_model" invisible="1"/>
                <field name="res_id" widget="generic_m2o" options="{'model_field': 'res_model'}"/>
            </form>
        `,
    });

    const input = queryOne(".o_field_widget[name='res_id'] input");
    expect(input.value).toBe("");
});


test("GenericMany2OneField in readonly mode", async () => {
    onRpc("name_get", () => {
        return [[1, "Partner 1"]];
    });

    await mountView({
        type: "form",
        resModel: "test.model",
        resId: 1,
        mode: "readonly",
        arch: `
            <form>
                <field name="res_model" invisible="1"/>
                <field name="res_id" widget="generic_m2o" options="{'model_field': 'res_model'}"/>
            </form>
        `,
    });

    await animationFrame();

    expect(".o_field_widget[name='res_id']").toHaveCount(1);
});


test("GenericMany2OneField in list view", async () => {
    onRpc("name_get", () => {
        return [[1, "Partner 1"]];
    });

    await mountView({
        type: "list",
        resModel: "test.model",
        arch: `
            <list>
                <field name="name"/>
                <field name="res_model" column_invisible="1"/>
                <field name="res_id" widget="generic_m2o" options="{'model_field': 'res_model'}"/>
            </list>
        `,
    });

    expect(".o_data_row").toHaveCount(2);
});
