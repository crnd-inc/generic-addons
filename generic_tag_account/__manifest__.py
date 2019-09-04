{
    'name': "Generic Tag (Account)",

    'summary': """
        Generic tag integration with account addon
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",

    'category': 'Generic Tags',
    'version': '11.0.1.0.12',

    "depends": [
        "generic_tag",
        "account",
    ],

    "data": [
        'data/generic_tag_model.xml',
        'views/account_invoice_view.xml',
        'views/tag_view.xml',
    ],
    'images': ['static/description/banner.png'],
    "installable": True,
    "auto_install": True,
    'license': 'LGPL-3',
}
