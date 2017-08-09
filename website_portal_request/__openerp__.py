# -*- coding: utf-8 -*-
{
    'name': 'Website Portal for Request',
    'category': 'Website',
    'summary': 'Generic request management',
    "author": "Management and Accounting Online",
    "license": "LGPL-3",
    'version': '9.0.1.0.0',
    'depends': [
        'website_portal_v10',
        'website_mail',
        'generic_request',
    ],
    'data': [
        'views/templates_mail_thread.xml',
        'views/templates.xml',
        'views/request_type_view.xml',
        'views/request_category_view.xml',
    ],
    'demo': [
        'demo/demo_category.xml',
        'demo/demo_generic_type.xml',
        'demo/demo_upgrade_type.xml',
    ],
    'installable': True,
    'auto_install': False,
}
