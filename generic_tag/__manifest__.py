{
    'name': "Generic Tag",

    'summary': """
        Generic tag management.
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",

    'category': 'Generic Tags',
    'version': '14.0.2.2.0',

    "depends": [
        "base",
    ],

    "data": [
        'security/base_security.xml',
        'security/ir.model.access.csv',
        'views/generic_tag_view.xml',
        'views/generic_tag_category_view.xml',
        'views/generic_tag_model_view.xml',
        'wizard/wizard_manage_tags.xml',
    ],
    'images': ['static/description/banner.png'],
    "installable": True,
    "application": True,
    'license': 'LGPL-3',
}
