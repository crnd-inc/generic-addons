from odoo.addons.generic_mixin.tools.migration_utils import (
    ensure_version,
    migrate_xmlids_to_module,
    cleanup_module_data,
)


@ensure_version('2.2.0')
def migrate(cr, installed_version):
    migrate_xmlids_to_module(
        cr,
        src_module='generic_location_tag',
        dst_module='generic_location',
        models=[
            'ir.model.fields',
            'ir.model.constraint',
            'ir.model.relation',
            'ir.ui.menu',
            'ir.model.access',
            'ir.actions.act_window',
            'generic.tag.model',
        ],
        cleanup=True,
    )
    migrate_xmlids_to_module(
        cr,
        src_module='generic_location_geo',
        dst_module='generic_location',
        models=[
            'ir.model.fields',
            'ir.model.constraint',
            'ir.model.relation',
            'ir.ui.menu',
            'ir.model.access',
            'ir.actions.act_window',
        ],
        cleanup=True,
    )

    # Migrate demo data
    migrate_xmlids_to_module(
        cr,
        src_module='generic_location_tag',
        dst_module='generic_location',
        models=[
            'generic.location',
            'generic.tag',
        ],
        cleanup=False,
    )

    # Cleanup module data
    cleanup_module_data(cr, 'generic_location_tag')
    cleanup_module_data(cr, 'generic_location_geo')
