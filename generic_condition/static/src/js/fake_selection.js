import { onPatched, proxy, t, useProps } from "@odoo/owl";
import { registry } from "@web/core/registry";
import {
    SelectionField,
    selectionField,
    selectionFieldProps,
} from "@web/views/fields/selection/selection_field";
import { useService } from "@web/core/utils/hooks";

class FakeSelection extends SelectionField {
    props = useProps({
        ...selectionFieldProps,
        selectionField: t.string().optional(),
    });

    static supportedTypes = ['char'];

    setup() {
        this.orm = useService('orm');

        this.state = proxy({
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
        // many2one values are {id, display_name} objects
        const id = selectionFieldValue.id;
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
