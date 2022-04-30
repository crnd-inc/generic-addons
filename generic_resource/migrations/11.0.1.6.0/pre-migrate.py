def migrate(cr, installed_version):
    cr.execute("""
        UPDATE ir_model_data
        SET module = 'generic_resource'
        WHERE module = 'generic_resource_role'
          AND name IN (
               'field_generic_resource_resource_visibility',
               'field_generic_resource_simple_resource_visibility',
               'field_generic_resource_type_resource_visibility',

               /* v12 compatability */
               'field_generic_resource__resource_visibility',
               'field_generic_resource_simple__resource_visibility',
               'field_generic_resource_type__resource_visibility')
    """)
