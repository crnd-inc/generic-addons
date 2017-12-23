{
    'name': "Generic Tag (Sale)",

    'summary': """
        Generic tag integration with sale addon
    """,

    'author': "Management and Accounting Online",
    'website': "https://maao.com.ua",

    'category': 'Generic Tags',
    'version': '11.0.0.1.0',

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
    "installable": True,
    "auto_install": True,
    'license': 'Other proprietary',
}
