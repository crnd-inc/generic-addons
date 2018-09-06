{
    'name': "Generic Tag",

    'summary': """
        Generic tag management.
    """,

    'author': "Center of Research & Development",
    'website': "https://crnd.pro",

    'category': 'Generic Tags',
    'version': '11.0.1.0.0',

    "depends": [
        "base",
    ],

    "data": [
        'security/base_security.xml',
        'security/ir.model.access.csv',
        'views/generic_tag_view.xml',
        'views/generic_tag_category_view.xml',
        'views/generic_tag_model_view.xml',
    ],
    "installable": True,
    "application": True,
    'license': 'LGPL-3',
}
