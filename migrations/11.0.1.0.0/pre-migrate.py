# -*- coding: utf-8 -*-


def migrate(cr, installed_version):
    cr.execute("""
        DROP TABLE IF EXISTS generic_resource_implementation CASCADE;
        DELETE FROM ir_model WHERE model = 'generic.resource.implementation';

        DROP TABLE IF EXISTS generic_resource_interface CASCADE;
        DELETE FROM ir_model WHERE model = 'generic.resource.interface';
    """)
