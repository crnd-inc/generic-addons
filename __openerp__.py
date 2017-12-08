{
    'name': "Generic Resource",

    'summary': """
    """,

    'author': "Management and Accounting Online",
    'website': "https://maao.com.ua",

    'category': 'Generic Resource',
    'version': '11.0.0.0.2',

    # any module necessary for this one to work correctly
    'depends': [
        'generic_m2o'
    ],

    # always loaded
    'data': [
        'data/ir_module_category.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/generic_resource_views.xml',
        'views/generic_resource_implementation_views.xml',
        'views/generic_resource_interface_views.xml',
        'views/generic_resource_type_views.xml'
    ],
    'demo': [
    ],
    'installable': True,
    'application': False,
    'license': 'Other proprietary',
}
