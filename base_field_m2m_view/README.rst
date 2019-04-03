Base Field Many2manyView
========================

.. |badge1| image:: https://img.shields.io/badge/GitHub-Base_Field_Many2manyView-green.png
    :target: https://github.com/crnd-inc/generic-addons/tree/11.0/base_field_m2m_view

.. |badge2| image:: https://img.shields.io/badge/license-LGPL--3-blue.png
    :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3

.. |badge5| image:: https://img.shields.io/badge/maintainer-CR&D-purple.png
    :target: https://crnd.pro/
    

|badge2| |badge5| |badge1|

*Base Field Many2many View* is a technical addon developed by the `Center of Research &
Development company <https://crnd.pro/>`__.

This addon adds new field ``Many2manyView``.
This field have only one difference from the standard ``Many2many`` field:
it does not create m2m relation table, but expects this table to be created somewhere outside.
Thus it allows to use another models as m2m-relation tables, or PostgreSQL Views.

At this time this addon is in *alpha* stage, thus use it on your own risk.

Usage
=====

1. Add *base_field_m2m_view* to dependency to your addon
2. Import field class ``from odoo.addons.base_field_m2m_view.fields import Many2manyView``
3. Declare field ``my_field = Many2manyView('my.model', 'my_relation_table', 'column1', 'column2')``

Also it is possible to use this field as: ``my_field = odoo.fields.Many2manyView(...)``

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
