/** @odoo-module **/

import {useState} from "@odoo/owl";
import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";
import {
    buildM2OFieldDescription,
    extractM2OFieldProps,
    Many2OneField,
} from '@web/views/fields/many2one/many2one_field';
import {Many2One} from "@web/views/fields/many2one/many2one";
import {useOwnedDialogs, useService} from "@web/core/utils/hooks";
import {sprintf} from "@web/core/utils/strings";
import {
    Many2XAutocomplete,
    useOpenMany2XRecord
} from "@web/views/fields/relational_utils";
import {
    SelectCreateDialog
} from "@web/views/view_dialogs/select_create_dialog";

const {onPatched} = owl;

function m2oTupleFromData(data) {
    if (!data) {
        return false;
    }
    const id = data.id;
    const displayName = data.display_name || data.displayName || data.name;
    return [id, displayName];
}

function useGenericSelectCreate({
                                    resModel,
                                    activeActions,
                                    onSelected,
                                    onCreateEdit
                                }) {
    const addDialog = useOwnedDialogs();

    function selectCreate({domain, context, filters, title, forceModel}) {
        if (typeof domain === "function") {
            domain = domain();
        }
        if (!Array.isArray(domain)) {
            domain = [];
        }
        addDialog(SelectCreateDialog, {
            title: title || _t("Select records"),
            noCreate: !activeActions.create,
            multiSelect: "link" in activeActions ? activeActions.link : false, // LPE Fixme
            resModel: forceModel || resModel,
            context,
            domain,
            onSelected,
            onCreateEdit: () => onCreateEdit({context}),
            dynamicFilters: filters,
        });
    }
    return selectCreate;
}

class GenericMany2XAutocomplete extends Many2XAutocomplete {
    setup() {
        super.setup(...arguments);
        const {activeActions, resModel, update} = this.props;
        this.selectCreate = useGenericSelectCreate({
            resModel,
            activeActions,
            onSelected: async (resId) => {
                const resIds = Array.isArray(resId) ? resId : [resId];
                const ids = resIds.filter((id) => typeof id === "number");
                if (!ids.length) {
                    return update([]);
                }
                const data = await this.orm.call(resModel, "name_get", [ids]);
                const values = data.map(([id, display_name]) => ({ id, display_name }));
                return update(values);
            },
            onCreateEdit: ({context}) => this.openMany2X({context}),
        });
    }

    async loadOptionsSource(request) {
        if (!this.props.resModel) {
            return [];
        }
        return await super.loadOptionsSource(...arguments);
    }

    async onSearchMore(request) {
        const {resModel, getDomain, context, fieldString} = this.props;

        const domain = getDomain();
        let dynamicFilters = [];
        if (request.length) {
            const nameGets = await this.orm.call(resModel, "name_search", [], {
                name: request,
                args: domain,
                operator: "ilike",
                limit: this.props.searchMoreLimit,
                context,
            });

            dynamicFilters = [
                {
                    description: sprintf(_t("Quick search: %s"), request),
                    domain: [["id", "in", nameGets.map((nameGet) => nameGet[0])]],
                },
            ];
        }

        const title = sprintf(_t("Search: %s"), fieldString);
        this.selectCreate({
            domain,
            context,
            filters: dynamicFilters,
            title,
            forceModel: resModel,
        });
    }
}

GenericMany2XAutocomplete.template = 'generic_m2o.GenericMany2XAutocomplete';

export class GenericMany2One extends Many2One {
    static template = "web.Many2One";
    static components = {
        ...Many2One.components,
        Many2XAutocomplete: GenericMany2XAutocomplete,
    };
}

export class GenericMany2OneField extends Many2OneField {
    static template = "generic_m2o.GenericMany2OneField";
    static supportedTypes = ['integer', 'many2one_reference']
    static components = {
        ...Many2OneField.components,
        GenericMany2One,
        GenericMany2XAutocomplete,
    };
    static props = {
        ...Many2OneField.props,
        modelField: {
            type: String,
            optional: true,
        },
    };

    setup() {
        super.setup(...arguments);
        this.state = useState({
            proxyDisplayName: false,
        });
        this.orm = useService("orm");
        this.modelField = this.props.modelField;
        if (!this.modelField) {
            const fieldName = this.props.name;
            const modelFieldFromFieldAttrs = this.props.record.fields[fieldName].model_field;
            if (modelFieldFromFieldAttrs) {
                this.modelField = modelFieldFromFieldAttrs;
            } else {
                throw new Error(`Field "${fieldName}" must have the "model_field" parameter`);
            }
        }
        if (!(this.modelField in this.props.record.data)) {
            throw new Error(`The field specified in parameter "model_field" was not found in the form view`);
        }
        onPatched(this.onPatched)
        this.currentRelationModel = this.relationModel;
        this.currentRecordId = this.props.record.id;
        this.updateProxyDisplayName();

        // Quick Create is disabled because it is not possible to correctly extend the 'web.BasicModel'
        this.quickCreate = null;

        this.openMany2X = useOpenMany2XRecord({
            resModel: this.relation,
            activeActions: {
                create: this.props.canCreate,
                createEdit: this.props.canCreateEdit,
                write: this.props.canWrite,
            },
            isToMany: false,
            onRecordSaved: async (record) => {
                await this.props.record.load();
                await this.proxyUpdate(m2oTupleFromData(record.data));
                if (this.props.record.model.root.id !== this.props.record.id) {
                    this.props.record.switchMode("readonly");
                }
            },
            onClose: () => this.focusInput(),
            fieldString: this.props.string,
        });

        this.update = (value, params = {}) => {
            if (value) {
                value = m2oTupleFromData(value[0]);
            }
            return this.proxyUpdate(value);
        };
    }

    get m2oProps() {
        const value = this.props.record.data[this.props.name];
        return {
            canCreate: this.props.canCreate,
            canCreateEdit: this.props.canCreateEdit,
            canOpen: this.props.canOpen,
            canQuickCreate: this.props.canQuickCreate,
            canScanBarcode: this.props.canScanBarcode,
            canWrite: this.props.canWrite,
            context: this.props.context,
            cssClass: this.props.className,
            domain: () => (typeof this.props.domain === "function" ? this.props.domain() : this.props.domain || []),
            id: this.props.id,
            linkCssClass: "",
            nameCreateField: this.props.nameCreateField,
            openActionContext: () => this.props.context,
            placeholder: this.props.placeholder,
            readonly: this.props.readonly,
            relation: this.relation,
            searchThreshold: this.props.searchThreshold,
            string: this.props.string,
            update: (idNamePair, options = {}) => {
                const resId = idNamePair ? idNamePair.id : false;
                if (idNamePair && idNamePair.display_name) {
                    this.state.proxyDisplayName = idNamePair.display_name;
                } else {
                    this.state.proxyDisplayName = false;
                }
                return this.props.record.update({ [this.props.name]: resId }, options);
            },
            value: value
                ? { id: value, display_name: this.state.proxyDisplayName || _t("Unnamed") }
                : false,
        };
    }

    onPatched() {
        let changedRelationModel = false;
        let changedRecord = false;
        if (this.currentRelationModel !== this.relationModel) {
            this.currentRelationModel = this.relationModel;
            changedRelationModel = true;
        }
        if (this.currentRecordId !== this.props.record.id) {
            this.currentRecordId = this.props.record.id;
            changedRecord = true;
        }
        if (changedRelationModel || changedRecord) {
            if (!changedRecord) {
                this.props.record.update(false);
            } else {
                this.updateProxyDisplayName();
            }
        }
    }

    updateProxyDisplayName(resId) {
        if (!resId) {
            resId = this.props.record.data[this.props.name];
        }
        if (!this.relationModel || !resId || typeof(resId) !== 'number'){
            return;
        }
        this.orm.call(this.relationModel, 'name_get', [[resId]])
            .then((data) => {
                this.state.proxyDisplayName = data[0][1];
            }).catch(() => {
                this.state.proxyDisplayName = false;
            });
    }

    get relationModel() {
        return this.props.record.data[this.modelField];
    }

    get relation() {
        return this.relationModel || this.props.record.data.res_model;
    }

    get displayName() {
        return (this.proxyValue && this.proxyValue[1]) ? this.proxyValue[1].split("\n")[0] : '';
    }

    get extraLines() {
        return this.displayName ? this.displayName.split("\n").map((line) => line.trim()).slice(1) : [];
    }

    get resId() {
        let val = this.proxyValue;
        return val && val[0];
    }

    async openDialog(resId) {
        return this.openMany2X({
            resId,
            forceModel: this.relationModel,
            context: this.context,
        });
    }

    get proxyValue() {
        const value = this.props.record.data[this.props.name];
        return value
            ? [value, this.state.proxyDisplayName]
            : false;
    }

    proxyUpdate(value) {
        let resId = false;
        let displayName = false;
        if (value) {
            displayName = value[1] || false;
            resId = value[0];
        }
        this.state.proxyDisplayName = displayName;
        if (!displayName) {
            this.updateProxyDisplayName(resId);
        }
        let vals = {};
        vals[this.props.name] = resId
        this.props.record.update(vals);
    }
}

export const genericMany2OneField = {
    ...buildM2OFieldDescription(GenericMany2OneField),
    supportedTypes: ['integer', 'many2one_reference'],
    extractProps(fieldInfo, dynamicInfo) {
        const props = {
            ...extractM2OFieldProps(...arguments),
            modelField: fieldInfo.attrs.model_field,
        }
        return props;
    },
};

registry.category('fields').add('generic_m2o', genericMany2OneField);
