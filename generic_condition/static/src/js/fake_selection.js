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

        this.state = useState({
            fakeOptions: [],
        });

        this.currentSelectionFieldId = this.selectionFieldId;
        this.updateFakeOptions();

        onPatched(() => {
            if (this.currentSelectionFieldId !== this.selectionFieldId) {
                this.currentSelectionFieldId = this.selectionFieldId;
                this.updateFakeOptions();
            }
        });
    }

    get options() {
        return this.state.fakeOptions;
    }

    get string() {
        const val = this.value;
        if (!val) {
            return '';
        }
        const option = this.options.find((o) => o[0] === val);
        return option ? option[1] : '';
    }

    get selectionFieldId() {
        if (!this.props.selectionField) {
            return false;
        }
        const selectionFieldValue = this.props.record.data[this.props.selectionField];
        if (!selectionFieldValue) {
            return false;
        }
        // In Odoo 19+, many2one values are {id, display_name} objects;
        // in older versions they were [id, name] arrays.
        const id = selectionFieldValue.id || selectionFieldValue[0];
        if (!id) {
            return false;
        }
        return id;
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

    onChange(value) {
        this.props.record.update(
            { [this.props.name]: value ?? false },
            { save: this.props.autosave }
        );
    }
}

FakeSelection.extractProps = (staticInfo, dynamicInfo) => {
    return {
        ...selectionField.extractProps(staticInfo, dynamicInfo),
        selectionField: (staticInfo.attrs && staticInfo.attrs.selection_field) || '',
    };
};

registry.category('fields').add('fake_selection', {
    ...selectionField,
    supportedTypes: ['char'],
    component: FakeSelection,
    extractProps: FakeSelection.extractProps,
});
