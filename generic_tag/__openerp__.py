# -*- coding: utf-8 -*-
{
    'name': "Generic Tag",

    'summary': """
        Generic tag management.
    """,

    'author': "Management and Accounting Online",
    'website': "https://maao.com.ua",

    'category': 'Uncategorized',
    'version': '9.0.0.1.0',

    "depends": [
        "base",
        "base_action_rule",
    ],

    "data": [
        'security/base_security.xml',
        'security/ir.model.access.csv',
        'views/generic_tag_view.xml',
        'views/generic_tag_category_view.xml',
        'views/generic_tag_model_view.xml',
    ],
    "installable": True,
    'license': 'Other proprietary',
}
