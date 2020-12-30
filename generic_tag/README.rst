Generic Tag
===========


.. |badge1| image:: https://img.shields.io/badge/pipeline-pass-brightgreen.png
    :target: https://github.com/crnd-inc/generic-addons

.. |badge2| image:: https://img.shields.io/badge/license-LGPL--3-blue.png
    :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3

.. |badge3| image:: https://img.shields.io/badge/powered%20by-yodoo.systems-00a09d.png
    :target: https://yodoo.systems
    
.. |badge5| image:: https://img.shields.io/badge/maintainer-CR&D-purple.png
    :target: https://crnd.pro/
    
.. |badge4| image:: https://img.shields.io/badge/docs-Generic_Tag-yellowgreen.png
    :target: https://crnd.pro/doc-bureaucrat-itsm/11.0/en/Generic_Tag_admin_eng

.. |badge6| image:: https://img.shields.io/badge/GitHub-Generic_Tag-green.png
    :target: https://github.com/crnd-inc/generic-addons/tree/11.0/generic_tag


|badge1| |badge2| |badge4| |badge5| |badge6|
    


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
You can try it by the references below.

Launch your own ITSM system in 60 seconds:
''''''''''''''''''''''''''''''''''''''''''

Create your own `Bureaucrat ITSM <https://yodoo.systems/saas/template/bureaucrat-itsm-demo-data-95>`__ database

|badge3| 

Usage:
''''''

To add tags to your model do the folowing simple steps:

1. Add `generic_tag` module as dependency for your addon.

2. Use inherit from `"generic.tag.mixin"` to get *tags* functionality to your model, like:

    .. code:: python

        class Product(models.Model):
            _name = "product.product"
            _inherit = [
                "product.product",
                "generic.tag.mixin",
            ]
 
3. Add record to taggable models registry:

    .. code:: xml

        <record model="generic.tag.model" id="generic_tag_model_product_product">
            <field name="res_model_id" ref="product.model_product_product"/>
        </record>

4. Now you can use ``tag_ids`` field in your views for your model:

  - `search` view:

    .. code:: xml

        <field name="tag_ids"/>
        <field name="search_tag_id"/> <!-- For direct searching (items that contain selected tag)-->
        <field name="search_no_tag_id"/> <!-- For inverse searching (items that do not contain selected tag)-->

    See `search_tag_id` and `search_no_tag_id` fields.
    These fields add autocompletition on searching by specific tag.
    `search_tag_id` allows to search for records that contain selected tag.
    `search_no_tag_id` allows to search for records that have no selected tag.

  - `tree` view:

    .. code:: xml

        <field name="tag_ids"
               widget="many2many_tags"
               placeholder="Tags..."
               options="{'color_field': 'color'}"/>

  - `form` view:

    .. code:: xml

        <field name="tag_ids"
               widget="many2many_tags"
               placeholder="Tags..."
               context="{'default_model': 'product.product'}"
               options="{'color_field': 'color'}"/>

    Pay attention on context field. This will automatically select correct model on tag creation.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/crnd-inc/generic-addons/issues>`_.
In case of trouble, please check there if your issue has already been reported.


Maintainer
''''''''''
.. image:: https://crnd.pro/web/image/3699/300x140/crnd.png

Our web site: https://crnd.pro/

This module is maintained by the `Center of Research &
Development company <https://crnd.pro/>`__.

We can provide you further Odoo Support, Odoo implementation, Odoo customization, Odoo 3rd Party development and integration software, consulting services. Our main goal is to provide the best quality product for you. 

For any questions `contact us <mailto:info@crnd.pro>`__.




