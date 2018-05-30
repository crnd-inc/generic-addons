{
    'name': "Generic Location",

    'summary': """
    """,

    'author': "Center of Research & Development",
    'website': "https://crnd.pro",

    'category': 'Generic Location',
    'version': '11.0.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['generic_mixin', 'mail'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/generic_location.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo_location.xml'
    ],
    'installable': True,
    'application': False,
    'license': 'Other proprietary',
}
