# -*- coding: utf-8 -*-
{
    'name': "Generic Resource",

    'summary': """
    """,

    'author': "Center of Research & Development",
    'website': "https://crnd.pro",

    'category': 'Generic Resource',
    'version': '10.0.0.1.2',

    # any module necessary for this one to work correctly
    'depends': [
        'mail',
        'generic_m2o',
        'generic_mixin',
    ],

    # always loaded
    'data': [
        'data/ir_module_category.xml',

        'security/security.xml',
        'security/ir.model.access.csv',

        'data/generic_resource_type_data.xml',
        'data/ir_sequence_data.xml',

        'views/generic_resource_views.xml',
        'views/generic_resource_implementation_views.xml',
        'views/generic_resource_interface_views.xml',
        'views/generic_resource_type_views.xml',
        'views/generic_resource_simple.xml',
        'views/generic_resource_simple_category.xml',
    ],
    'demo': [
        'demo/demo_resource.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'Other proprietary',
}
