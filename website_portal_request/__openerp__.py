# -*- coding: utf-8 -*-
{
    'name': 'Website Portal for Request',
    'category': 'Website',
    'summary': 'Generic request management',
    "author": "Management and Accounting Online",
    "license": "LGPL-3",
    'version': '10.0.1.0.0',
    'depends': [
        'website_portal',
        'website_mail',
        'generic_request',
    ],
    'data': [
        'views/templates_mail_thread.xml',
        'views/templates.xml',
    ],
    'installable': True,
    'auto_install': False,
}
