/** @odoo-module **/

import { expect, test } from "@odoo/hoot";
import { queryAll } from "@odoo/hoot-dom";
import { advanceTime, animationFrame } from "@odoo/hoot-mock";
import {
    defineModels,
    fields,
    models,
    mountView,
} from "@web/../tests/web_test_helpers";

import {
    gmrvHighlightStore,
    gmrvSetHighlight,
} from "@generic_mixin/js/gmrv_highlight";

const CLASS_CREATE = "gmrv_highlighting_record_create";
const CLASS_WRITE = "gmrv_highlighting_record_write";

class GmrvTestModel extends models.Model {
    _name = "gmrv.test.model";

    name = fields.Char();

    _records = [
        { id: 1, name: "Created record" },
        { id: 2, name: "Updated record" },
        { id: 3, name: "Untouched record" },
    ];
}

defineModels([GmrvTestModel]);

/** Reset the store, thus tests do not affect each other */
function resetHighlight() {
    gmrvHighlightStore.records = {};
}

test("list view: highlight created and updated records", async () => {
    resetHighlight();
    await mountView({
        type: "list",
        resModel: "gmrv.test.model",
        arch: `<list><field name="name"/></list>`,
    });

    const rows = () => queryAll(".o_data_row");
    expect(rows()).toHaveLength(3);
    expect(`.o_data_row.${CLASS_CREATE}`).toHaveCount(0);
    expect(`.o_data_row.${CLASS_WRITE}`).toHaveCount(0);

    gmrvSetHighlight({
        "gmrv.test.model": { create: [1], write: [2] },
    });
    await animationFrame();

    expect(rows()[0]).toHaveClass(CLASS_CREATE);
    expect(rows()[1]).toHaveClass(CLASS_WRITE);
    expect(rows()[2]).not.toHaveClass(CLASS_CREATE);
    expect(rows()[2]).not.toHaveClass(CLASS_WRITE);
});

test("list view: highlighting is removed after timeout", async () => {
    resetHighlight();
    await mountView({
        type: "list",
        resModel: "gmrv.test.model",
        arch: `<list><field name="name"/></list>`,
    });

    gmrvSetHighlight({
        "gmrv.test.model": { create: [1], write: [] },
    });
    await animationFrame();
    expect(`.o_data_row.${CLASS_CREATE}`).toHaveCount(1);

    await advanceTime(1300);
    await animationFrame();
    expect(`.o_data_row.${CLASS_CREATE}`).toHaveCount(0);
});

test("list view: records of other models are not highlighted", async () => {
    resetHighlight();
    await mountView({
        type: "list",
        resModel: "gmrv.test.model",
        arch: `<list><field name="name"/></list>`,
    });

    gmrvSetHighlight({
        "gmrv.other.model": { create: [1], write: [2] },
    });
    await animationFrame();

    expect(`.o_data_row.${CLASS_CREATE}`).toHaveCount(0);
    expect(`.o_data_row.${CLASS_WRITE}`).toHaveCount(0);
});

test("kanban view: highlight created and updated records", async () => {
    resetHighlight();
    await mountView({
        type: "kanban",
        resModel: "gmrv.test.model",
        arch: `
            <kanban>
                <templates>
                    <t t-name="card">
                        <field name="name"/>
                    </t>
                </templates>
            </kanban>`,
    });

    const cards = () => queryAll(".o_kanban_record:not(.o_kanban_ghost)");
    expect(cards()).toHaveLength(3);

    gmrvSetHighlight({
        "gmrv.test.model": { create: [1], write: [2] },
    });
    await animationFrame();

    expect(cards()[0]).toHaveClass(CLASS_CREATE);
    expect(cards()[1]).toHaveClass(CLASS_WRITE);
    expect(cards()[2]).not.toHaveClass(CLASS_CREATE);
    expect(cards()[2]).not.toHaveClass(CLASS_WRITE);
});
