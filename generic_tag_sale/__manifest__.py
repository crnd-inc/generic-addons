{
    'name': "Generic Tag (Sale)",

    'summary': """
        Generic tag integration with sale addon
    """,

    'author': "Center of Research & Development",
    'website': "https://crnd.pro",

    'category': 'Generic Tags',
    'version': '12.0.0.1.8',

    "depends": [
        "generic_tag",
        "payment",  # sale depends on payment addon,
                    # that is not installed automatically
        "sale",
    ],

    "data": [
        'data/generic_tag_model.xml',
        'views/sale_order_view.xml',
        'views/sale_order_line_view.xml',
        'views/tag_view.xml',
    ],
    'images': ['static/description/banner.png'],
    "installable": False,
    "auto_install": False,
    'license': 'LGPL-3',
}
