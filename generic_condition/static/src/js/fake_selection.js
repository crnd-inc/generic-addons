/** @odoo-module **/

import { registry } from "@web/core/registry";
import { SelectionField, selectionField } from "@web/views/fields/selection/selection_field";
import { useService } from "@web/core/utils/hooks";

const { useState, onPatched } = owl;

class FakeSelection extends SelectionField {
    static props = {
        ...SelectionField.props,
        selectionField: { type: String, optional: true },
    };

    static supportedTypes = ['char'];

    setup() {
        this.orm = useService('orm');

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
        if (this.props.value === false) {
            return '';
        }
        const option = this.options.find((o) => o[0] === this.props.value);
        return option ? option[1] : '';
    }

    get selectionFieldId() {
        if (!this.props.selectionField) {
            return false;
        }
        const selectionFieldValue = this.props.record.data[this.props.selectionField];
        if (!selectionFieldValue || !selectionFieldValue[0]) {
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

    async updateFakeOptions() {
        if (!this.selectionFieldId) {
            this.state.fakeOptions = [];
            return;
        }
        try {
            const data = await this.orm.call(
                'ir.model.fields',
                'get_field_selections',
                [[this.selectionFieldId]],
            );
            this.state.fakeOptions = data || [];
        } catch (error) {
            console.warn('Failed to fetch field selections:', error);
            this.state.fakeOptions = [];
        }
    }

    onChange(ev) {
        const value = JSON.parse(ev.target.value);
        this.props.record.update(
            { [this.props.name]: value },
            { save: this.props.autosave }
        );
    }
}

FakeSelection.extractProps = ({ attrs, viewType }, dynamicInfo) => {
    return {
        ...selectionField.extractProps({ attrs, viewType }, dynamicInfo),
        selectionField: attrs.selection_field || '',
    };
};

registry.category('fields').add('fake_selection', {
    ...selectionField,
    component: FakeSelection,
    extractProps: FakeSelection.extractProps,
});
