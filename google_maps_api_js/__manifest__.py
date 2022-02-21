{
    'name': "CR&D Map View",
    'author': "Center of Research and Development",
    'website': "https://crnd.pro",
    'license': 'Other proprietary',
    'version': '14.0.0.1.0',

    'depends': [
        'base_geolocalize',
    ],

    'data': [
        'template/template.xml',
    ],

    'qweb': [
        'static/src/xml/map_view.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': True,
}
