# -*- coding: utf-8 -*-


def migrate(cr, installed_version):
    cr.execute("""
        UPDATE ir_model_data
        SET module='generic_resource'
        WHERE module = 'generic_resource_simple'
          AND model in ('generic.resource',
                        'generic.resource.type',
                        'generic.resource.simple',
                        'generic.resource.simple.category',
                        'ir.model',
                        'ir.model.fields',
                        'ir.ui.menu',
                        'ir.ui.view',
                        'ir.sequence',
                        'ir.actions.act_window');
    """)
