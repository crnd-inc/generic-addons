{
    'name': "Generic Tag (Sale)",

    'summary': """
        Generic tag integration with sale addon
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",

    'category': 'Generic Tags',
    'version': '11.0.0.1.13',

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
    "installable": True,
    "auto_install": False,
    'license': 'LGPL-3',
}
