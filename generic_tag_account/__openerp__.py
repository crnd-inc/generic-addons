# -*- coding: utf-8 -*-
{
    'name': "Generic Tag (Account)",

    'summary': """
        Generic tag integration with account addon
    """,

    'author': "Management and Accounting Online",
    'website': "https://maao.com.ua",

    'category': 'Generic Tags',
    'version': '11.0.0.1.0',

    "depends": [
        "generic_tag",
        "account",
    ],

    "data": [
        'data/generic_tag_model.xml',
        'views/account_invoice_view.xml',
        'views/tag_view.xml',
    ],
    "installable": True,
    "auto_install": True,
    'license': 'Other proprietary',
}
