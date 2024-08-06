{
    'name': "Generic Location",

    'summary': """
        Allows you to make an abstract description of the
        objects location relative to the general location
        (for example: house3 -> office5 -> room2 -> table5)""",

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",

    'category': 'Generic Location',
    'version': '17.0.2.11.2',

    # any module necessary for this one to work correctly
    'depends': [
        'base_field_m2m_view',
        'generic_mixin',
        'generic_tag',
        'mail',
    ],

    # always loaded
    'data': [
        'data/generic_tag_model.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/generic_location.xml',
        'views/generic_location_type.xml',
        'views/generic_location_tag_menu.xml',
        'views/res_config_settings.xml',
        'views/res_partner.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo_location.xml',
        'demo/demo_location_tag.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    "license": "LGPL-3",
}
