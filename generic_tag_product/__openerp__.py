# -*- coding: utf-8 -*-
{
    'name': "Generic Tag (Product) (Experimental) ",

    'summary': """
        Generic tag integration with product addon
    """,

    'author': "Management and Accounting Online",
    'website': "https://maao.com.ua",

    'category': 'Uncategorized',
    'version': '9.0.0.1.0',

    "depends": [
        "generic_tag",
        "product",
    ],

    "data": [
        'data/generic_tag_model.xml',
        'views/product.xml',
        'views/generic_tag_product.xml'
    ],
    "installable": True,
    "auto_install": False,
    'license': 'Other proprietary',
}