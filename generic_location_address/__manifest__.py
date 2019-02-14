{
    'name': "Generic Location (Address)",

    'summary': "Generic Location (Add address fields to *Generic Locations*)",

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",

    'category': 'Generic Location',
    'version': '12.0.1.0.11',

    # any module necessary for this one to work correctly
    'depends': [
        'generic_location',
    ],

    # always loaded
    'data': [
        'views/generic_location.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/generic_location.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
