{
    'name': "Generic Service",

    'summary': """
        The module allows you to create various services,
        which can then be used in other Odoo applications
        and modules.
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",
    'category': 'Generic Service',
    'version': '11.0.1.3.5',

    # any module necessary for this one to work correctly
    'depends': [
        'mail',
        'generic_mixin',
    ],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/generic_service_views.xml',
        'views/generic_service_level_views.xml',
        'views/res_partner_views.xml',
        'data/generic_service_default.xml'
    ],
    'demo': [
        'demo/generic_service_demo.xml',
        'demo/generic_service_level_demo.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'license': 'OPL-1',
}
