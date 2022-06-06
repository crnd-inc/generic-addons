def migrate(cr, installed_version):
    cr.execute("""
         UPDATE generic_service
         SET lifecycle_state = 'active'
         WHERE active = True
           AND lifecycle_state = 'draft';

         UPDATE generic_service
         SET lifecycle_state = 'archived'
         WHERE active = False
           AND lifecycle_state = 'draft';
    """)
