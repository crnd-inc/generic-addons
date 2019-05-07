{
    'name': "Generic Location Tag",

    'summary': """
        This addon provides integration betwen *Generic
        Location* and *Generic Tag* addons""",

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",

    'category': 'Generic Location',
    'version': '12.0.1.0.11',

    # any module necessary for this one to work correctly
    'depends': ['generic_location', 'generic_tag'],

    # always loaded
    'data': [
        'data/generic_tag_model.xml',
        'views/generic_location_tag_menu.xml',
        'views/generic_location_tag.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo_location_tag.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
