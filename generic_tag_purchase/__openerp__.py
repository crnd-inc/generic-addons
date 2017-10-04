# -*- coding: utf-8 -*-
{
    'name': "Generic Tag (Purchase)",

    'summary': """
        Generic tag integration with purchase addon
    """,

    'author': "Management and Accounting Online",
    'website': "https://maao.com.ua",

    'category': 'Generic Tags',
    'version': '11.0.0.1.0',

    "depends": [
        "generic_tag",
        "purchase",
    ],

    "data": [
        'data/generic_tag_model.xml',
        'views/purchase_order.xml',
        'views/purchase_order_line.xml',
        'views/generic_tag_purchase.xml'
    ],
    "installable": True,
    "auto_install": True,
    'license': 'Other proprietary',
}
