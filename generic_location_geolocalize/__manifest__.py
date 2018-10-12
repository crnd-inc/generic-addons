{
    'name': "Generic Location (Geo Localization)",

    'summary': """
    """,

    'author': "Center of Research & Development",
    'website': "https://crnd.pro",

    'category': 'Generic Location',
    'version': '11.0.1.0.2',

    # any module necessary for this one to work correctly
    'depends': [
        'generic_location_geo',
        'generic_location_address',
        'base_geolocalize',
    ],

    # always loaded
    'data': [
        'views/generic_location.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
