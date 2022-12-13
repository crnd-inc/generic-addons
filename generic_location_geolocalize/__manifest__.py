# flake8: noqa: E501
{
    'name': "Generic Location (Geo Localization)",

    'summary': """
        Generic Location (Automaticaly determine geo coordinates
        for location by its address)""",

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",

    'category': 'Generic Location',
    'version': '16.0.1.5.0',

    # any module necessary for this one to work correctly
    'depends': [
        'generic_location_geo',
        'base_geolocalize',
        'google_maps_api_js',
    ],

    # always loaded
    'data': [
        'views/generic_location.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],

    'assets': {
        'web.assets_backend': [
            '/generic_location_geolocalize/static/src/scss/map_field_widget.scss',
            '/generic_location_geolocalize/static/src/js/map_field_widget.js',
        ],
        'web.assets_qweb': [
            '/generic_location_geolocalize/static/src/xml/map_field_widget.xml',
        ],
    },
    'images': ['static/description/banner.png'],
    'installable': False,
    'application': False,
    'license': 'LGPL-3',
}
