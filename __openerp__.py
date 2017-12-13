# -*- coding: utf-8 -*-
{
    'name': "Generic Service",

    'summary': """
    """,

    'author': "Management and Accounting Online",
    'website': "https://maao.com.ua",

    'category': 'Generic Service',
    'version': '9.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'product'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/generic_service_views.xml',
        'data/generic_service_default.xml'
    ],
    'demo': [
        'demo/generic_service_demo.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'Other proprietary',
}
