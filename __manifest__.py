{
    'name': "Generic Resource",

    'summary': """
        Provides the ability to create and categorize
        various resources that can be used in other Odoo modules.
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",

    'category': 'Generic Resource',
    'version': '12.0.1.8.0',

    # any module necessary for this one to work correctly
    'depends': [
        'mail',
        'generic_m2o',
        'generic_mixin',
        'base_field_m2m_view',
    ],

    # always loaded
    'data': [
        'data/ir_module_category.xml',

        'security/security.xml',
        'security/ir.model.access.csv',

        'data/ir_sequence_data.xml',

        'views/ir_model.xml',
        'views/generic_resource_views.xml',
        'views/generic_resource_type_views.xml',
        'views/generic_resource_simple.xml',
        'views/generic_resource_simple_category.xml',
        'views/assets.xml',

        'data/generic_resource_type_data.xml',
    ],
    'demo': [
        'demo/demo_resource.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'license': 'OPL-1',
}
