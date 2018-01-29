# -*- coding: utf-8 -*-


def migrate(cr, installed_version):
    cr.execute("""
        UPDATE ir_model_data
        SET module='generic_resource'
        WHERE module = 'generic_resource_simple'
          AND model in ('generic.resource',
                        'generic.resource.simple',
                        'generic.resource.simple.category');
        UPDATE ir_model_data
        SET module='generic_resource'
        WHERE module = 'generic_resource_simple'
          AND name IN ('generic_resource_type_default',
                       'generic_resource_simple_sequence');
    """)
