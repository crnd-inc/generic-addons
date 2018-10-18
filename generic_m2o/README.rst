Generic Many2one Widget
=======================

.. |badge1| image:: https://img.shields.io/badge/pipeline-pass-brightgreen.png
    :target: https://github.com/crnd-inc/generic-addons

.. |badge2| image:: https://img.shields.io/badge/license-LGPL--3-blue.png
    :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3

|badge1| |badge2|

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



This module is part of the Bureaucrat ITSM project. 
You can try demo database by the reference: https://yodoo.systems/saas/template/itsm-16


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

For any questions contact us: info@crnd.pro 

