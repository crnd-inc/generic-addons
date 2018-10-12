Generic Many2one Widget
=======================

Make it easy to choose rignt records on generic many2one fields.
For example some where user can separately select name of model,
and choose ID of record for selected model. With this widget such case
as simple as usual many2one fields.

Usage
=====

Python fields declaration::

    model = fields.Char(string='Model')      # ex. 'res.partner'
    object_id = fields.Integer("Resource")   # ex. 42

XML fields declaration::

    <field name="model" invisible="1" />
    <field name="object_id" widget="generic_m2o" model_field="model" />


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/crnd-inc/generic-addons/issues>`_.
In case of trouble, please check there if your issue has already been reported.


Maintainer
''''''''''
.. image:: https://crnd.pro/web/image/3699/150x50xcrnd.png.pagespeed.ic.LZU01Bt1j0.webp

Our web site: https://crnd.pro/

This module is maintained by the Center of Research & Development company.

We can provide you further Odoo Support, Odoo implementation, Odoo customization, Odoo 3rd Party development and integration software, consulting services. Our main goal is to provide the best quality product for you. 

For any questions contact us: info@crnd.pro 

