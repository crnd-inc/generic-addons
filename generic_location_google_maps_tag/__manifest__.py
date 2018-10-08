{
    'name': "Generic Location (Google Maps + Tags)",

    'summary': """
        Integration addon
    """,

    'author': "Center of Research & Development",
    'website': "https://crnd.pro",

    'category': 'Generic Location',
    'version': '11.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'generic_location_google_maps',
        'generic_location_tag',
    ],

    # always loaded
    'data': [
        'views/generic_location.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'auto_install': True,
    'application': False,
    'license': 'LGPL-3',
}