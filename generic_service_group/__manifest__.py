{
    'name': "Generic Service Group",

    'summary': """
        Generic Service Group.
    """,

    'author': "Center of Development",
    'website': "https://crnd.pro",

    'category': 'Generic Group',
    'version': '12.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'generic_service',
        'generic_mixin',

    ],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/generic_service_group.xml',
    ],
    'demo': [
    ],
    'images': [],
    'installable': True,
    'application': False,
    'license': 'OPL-1',
    'auto_install': True,
    'price': 50.0,
    'currency': 'EUR',
}
