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
    'version': '11.0.1.2.6',

    # any module necessary for this one to work correctly
    'depends': [
        'mail',
    ],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/generic_service_views.xml',
        'data/generic_service_default.xml'
    ],
    'demo': [
        'demo/generic_service_demo.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'license': 'OPL-1',
}
