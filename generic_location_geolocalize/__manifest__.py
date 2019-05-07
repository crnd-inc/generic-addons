{
    'name': "Generic Location (Geo Localization)",

    'summary': """
        Generic Location (Automaticaly determine geo coordinates
        for location by its address)""",

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",

    'category': 'Generic Location',
    'version': '12.0.1.0.11',

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
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
