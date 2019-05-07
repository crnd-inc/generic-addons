Base Field BigInt Module
========================

.. |badge1| image:: https://img.shields.io/badge/GitHub-Base_Field_BigInt_Module-green.png
    :target: https://github.com/crnd-inc/generic-addons/tree/11.0/base_field_big_int

.. |badge2| image:: https://img.shields.io/badge/license-LGPL--3-blue.png
    :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3

.. |badge5| image:: https://img.shields.io/badge/maintainer-CR&D-purple.png
    :target: https://crnd.pro/
    

|badge2| |badge5| |badge1|

*Base Field Big Int* is technical addon developed by the `Center of Research &
Development company <https://crnd.pro/>`__.

This addon can be used to store big numbers (greater than *2 147 483 647*) in database as number.

At this time this addon is in *alpha* stage, thus use it on your own risk.
See `this issue <https://github.com/odoo/odoo/issues/8437>`__ for more details on possible errors.

Usage
=====

1. Add *base_field_big_int* to dependency to your addon
2. Import field class ``from odoo.addons.base_field_big_int.field import BigInt``
3. Declare field ``my_field = BigInt('My Big Integer field')``

Also it is possible to use this field as: ``my_field = odoo.fields.BigInt()``

Known Bugs
==========

- *BigInt* fields are not supported in *xmlrpc*

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/crnd-inc/generic-addons/issues>`_.
In case of trouble, please check there if your issue has already been reported.


Maintainer
''''''''''
.. image:: https://crnd.pro/web/image/3699/300x140/crnd.png

Our web site: https://crnd.pro/

This module is maintained by the Center of Research & Development company.

We can provide you further Odoo Support, Odoo implementation, Odoo customization, Odoo 3rd Party development and integration software, consulting services. Our main goal is to provide the best quality product for you. 

For any questions `contact us <mailto:info@crnd.pro>`__.





