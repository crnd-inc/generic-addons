{
    'name': "Generic Location (Geo Localization)",

    'summary': """
        Generic Location (Automaticaly determine geo coordinates
        for location by its address)""",

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",

    'category': 'Generic Location',
    'version': '14.0.1.3.1',

    # any module necessary for this one to work correctly
    'depends': [
        'generic_location_geo',
        'base_geolocalize',
        'google_maps_api_js',
    ],

    # always loaded
    'data': [
        'template/template.xml',
        'views/generic_location.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],

    'qweb': [
        'static/src/xml/map_field_widget.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
