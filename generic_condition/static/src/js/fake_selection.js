/** @odoo-module **/

import { registry } from "@web/core/registry";
import {
    SelectionField
} from "@web/views/fields/selection/selection_field";

const { useState, onPatched } = owl;

class FakeSelection extends SelectionField {
    setup() {
        onPatched(this.onPatched);

        this.state = useState({
            fakeOptions: [],
        });

        this.currentSelectionFieldId = this.selectionFieldId;
        this.updateFakeOptions();
    }

    get options() {
        return this.state.fakeOptions;
    }
    get string() {
        return this.props.value !== false
            ? this.options.find((o) => o[0] === this.props.value)[1]
            : '';
    }

    get selectionFieldId() {
        if (!this.props.selectionField) {
            return false;
        }
        const selectionFieldValue = this.props.record.data[this.props.selectionField];
        if (!selectionFieldValue) {
            return false;
        }
        return selectionFieldValue[0];
    }

    onPatched() {
        if (this.currentSelectionFieldId !== this.selectionFieldId) {
            this.currentSelectionFieldId = this.selectionFieldId;
            this.updateFakeOptions();
        }
    }

    updateFakeOptions() {
        if (!this.selectionFieldId) {
            this.state.fakeOptions = [];
        }
        this.env.model.orm.call(
            'ir.model.fields',
            'get_field_selections',
            [[this.selectionFieldId]],
        ).then((data) => {
            this.state.fakeOptions = data;
        }).guardedCatch(() => {
            this.state.fakeOptions = [];
        })
    }

    onChange(ev) {
        const value = JSON.parse(ev.target.value);
        this.props.update(value);
    }
}

FakeSelection.supportedTypes = ['char'];

FakeSelection.props = {
    ...SelectionField.props,
    selectionField: String,
};

FakeSelection.extractProps = ({ attrs }) => {
    return {
        ...SelectionField.extractProps,
        selectionField: attrs.selection_field,
    };
};

registry.category('fields').add('fake_selection', FakeSelection);
