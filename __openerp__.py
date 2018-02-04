# -*- coding: utf-8 -*-
{
    'name': "Generic Service",

    'summary': """
    """,

    'author': "Center of Research & Development",
    'website': "https://crnd.pro",

    'category': 'Generic Service',
    'version': '10.0.0.0.2',

    # any module necessary for this one to work correctly
    'depends': [
        'product'
    ],

    # always loaded
    'data': [
        'security/security.xml',
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
