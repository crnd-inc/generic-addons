Generic Tag
===========


.. |badge1| image:: https://img.shields.io/badge/pipeline-pass-brightgreen.png
    :target: https://github.com/crnd-inc/generic-addons

.. |badge2| image:: https://img.shields.io/badge/license-LGPL--3-blue.png
    :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3

|badge1| |badge2|
    


Generic Tag is a module developed by the `Center of Research &
Development company <https://crnd.pro/>`__. It allows you to create and categorize generic tags
(keywords).

With these tags in other applications, you can use the logic associated
with them (for example, search and filter objects by tags).

Integration with other modules is realized with the help of additional
modules.

Main features of the Generic Tag module:
''''''''''''''''''''''''''''''''''''''''

-  *Customize your own categories of tags.*
-  *Create and set up your unique (or completely generic) tags.*
-  *Associate your products, documents, contacts, etc. with created
   tags.*
-  *Use your tags!*


More information read in the `Generic Tag Module Guide <https://crnd.pro/doc-bureaucrat-itsm/11.0/en/Generic_Tag_admin_eng/>`__.


This module is part of the Bureaucrat ITSM project.
You can try demo database by the reference: https://yodoo.systems/saas/template/itsm-16

Usage:
''''''

To add tags to your model do the folowing simple steps:

1. Add base_tags module as dependency for your module.

2. Use inherit from "res.tag.mixin" to get tags functionality to your model, like:

    .. code:: python

      class Product(model.Model):
          _name = "product.product"
          _inherit = ["product.product",
                      "generic.tag.mixin"]
 
3. Add record to taggable models registry:

    .. code::

      <record model="generic.tag.model" id="generic_tag_model_product_product">
        <field name="res_model_id" ref="product.model_product_product"/>
      </record>

4. Now you can use tag_ids field in your views for your model:

  - search view:

    .. code::

      <field name="tag_ids"/>
      <field name="search_tag_id"/> <!-- For direct searching (items that contain selected tag)-->
      <field name="search_no_tag_id"/> <!-- For inverse searching (items that do not contain selected tag)-->

  - tree view:

    .. code::

      <field name="tag_ids" widget="many2many_tags" placeholder="Tags..."/>

  - form view:

    .. code::

      <field name="tag_ids"
             widget="many2many_tags"
             placeholder="Tags..."
             context="{'default_model': 'product.product'}"/>

    Pay attention on context field. This will automatically select correct model on tag creation.


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




