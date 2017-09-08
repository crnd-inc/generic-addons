# -*- coding: utf-8 -*-
{
    'name': "Generic Tag (Purchase)",

    'summary': """
        Generic tag integration with purchase addon
    """,

    'author': "Management and Accounting Online",
    'website': "https://maao.com.ua",

    'category': 'Uncategorized',
    'version': '9.0.0.1.0',

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
    "active": True,
    'license': 'Other proprietary',
}
