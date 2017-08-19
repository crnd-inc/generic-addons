# -*- coding: utf-8 -*-
{
    'name': "Generic Resource",

    'summary': """
    """,

    'author': "Management and Accounting Online",
    'website': "https://maao.com.ua",

    'category': 'Generic Request',
    'version': '9.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'generic_m2o'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/generic_resource_views.xml'
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': True,
    'application': False,
    'license': 'Other proprietary',
}
