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
