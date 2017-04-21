# -*- coding: utf-8 -*-
# © 2015-2016 Odoo S.A.
# © 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    'name': 'Website Portal for Request (Backported From v10)',
    'category': 'Website',
    'summary': 'Add your sales document in the frontend portal (sales order, '
               'quotations, invoices)',
    "author": "Management and Accounting Online",
    "license": "LGPL-3",
    'version': '9.0.1.0.0',
    'depends': [
        'website_portal_v10',
        'website_mail',
    ],
    'data': [
        'views/templates.xml',
    ],
    'installable': True,
    'auto_install': True,
}
