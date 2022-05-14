import inspect
from odoo import models, api


def generate_proxy_decorator(attr_name):
    """ Function to generate proxy decorator.
        Used to decorate methods that have to be proxied to model,
        that inherits from source model via delegation (delegate=True).
    """
    def proxy(fn):
        setattr(fn, attr_name, True)
        return fn
    return proxy


def proxy_method_wrapper(method_name, link_field):
    """ Generate proxy method for destination model, to call
        original method in original model

        :param str method_name: name of method in original model
            to call.
        :param str link_field: name of field to use to call
            original method
        :return callable: wrapped method, that will call original meth.
    """

    def method(self, *args, **kwargs):
        original_method = getattr(
            self.mapped(link_field), method_name)
        return original_method(*args, **kwargs)

    return method


class GenericMixinProxyMethods(models.AbstractModel):
    """ This mixin could be used in cases, when inheritance via delegation
        is used. In this case, it is common task, to make some methods
        defined on base model to be also available on inherited model.

        Usually it is applied to actions.

        For example, you have following structure:

            class MyBaseModel(models.Model):
                _name = 'my.base.model'

                base_field = fields.Char()

                def action_my_action(self):
                    for record in self:
                        # do something useful

            class MySpecificModelMixin(models.AbstractModel):
                _name = 'my.specific.model.mixin'

                base_record_id = fields.Many2one(
                    'my.base.model', delegate=True, required=True,
                    ondelete='cascade', readonly=True)

            class MySpecificModel1(models.Model):
                _name = 'my.specific.model.1'
                _inherit = 'my.specific.model.mixin'

                specific_field_1 = fields.Char()

            class MySpecificModel2(models.Model):
                _name = 'my.specific.model.2'
                _inherit = 'my.specific.model.mixin'

                specific_field_2 = fields.Char()

        In the example above, method 'action_my_action' is not available
        in MySpecificModel1 and MySpecificModel2, but it could be expected
        to be present, in case, if all these models share same base view.

        With this mixin, the example above could look like below:

            proxy_method = generate_proxy_decorator('__proxy_base_record__')

            class MyBaseModel(models.Model):
                _name = 'my.base.model'
                _inherit = [
                    'generic.mixin.proxy.methods',
                ]

                _generic_mixin_proxy_methods__dest_model = (
                    'my.specific.model.mixin')
                _generic_mixin_proxy_methods__link_field = 'base_record_id'
                _generic_mixin_proxy_methods__method_attr = (
                    '__proxy_base_record__')

                base_field = fields.Char()

                @proxy_method
                def action_my_action(self):
                    for record in self:
                        # do something useful

            class MySpecificModelMixin(models.AbstractModel):
                _name = 'my.specific.model.mixin'

                base_record_id = fields.Many2one(
                    'my.base.model', delegate=True, required=True,
                    ondelete='cascade', readonly=True)

            class MySpecificModel1(models.Model):
                _name = 'my.specific.model.1'
                _inherit = 'my.specific.model.mixin'

                specific_field_1 = fields.Char()

            class MySpecificModel2(models.Model):
                _name = 'my.specific.model.2'
                _inherit = 'my.specific.model.mixin'

                specific_field_2 = fields.Char()

        With this adjustments, method 'action_my_action' will be available in
        all specific models. And additionally, if we add new method to
        base model in new module and decorate it with 'proxy_method', then
        this new method will appear in all specific methods too.

        This is useful, if you want to create base model, with base views,
        and then be able to create multiple specific models based on base model
        and have ability to extend base model (and view) and be sure that
        changes will appear in specific models.

    """
    _name = 'generic.mixin.proxy.methods'
    _description = 'Generic Mixin: Proxy Methods'

    # Destination model to proxy methods to
    _generic_mixin_proxy_methods__dest_model = None

    # Name of field in dest_model, that have to be used to call original
    # methods. This field must be 'many2one' and 'delegate'
    _generic_mixin_proxy_methods__link_field = None

    # Name of method/func attr to check if it have to be proxy
    _generic_mixin_proxy_methods__method_attr = None

    @api.model
    def _setup_complete(self):
        """ Setup recomputation triggers, and complete the model setup. """
        res = super()._setup_complete()

        if self._name == 'generic.mixin.proxy.methods':
            return res

        if not self._generic_mixin_proxy_methods__dest_model:
            return res

        if not self._generic_mixin_proxy_methods__method_attr:
            return res

        if not self._generic_mixin_proxy_methods__link_field:
            return res

        mixin_cls = type(
            self.env[self._generic_mixin_proxy_methods__dest_model])

        def is_proxy_method(func):
            """ Check if function is marked as proxy
            """
            if not inspect.isfunction(func):
                return False
            return getattr(
                func, self._generic_mixin_proxy_methods__method_attr, False)

        # Find all proxy methods, and proxy them to dest model
        for attrname, __ in inspect.getmembers(type(self), is_proxy_method):
            if hasattr(mixin_cls, attrname):
                # We do not want to do anything if corresponding method
                # already exists on destination model
                continue
            setattr(
                mixin_cls,
                attrname,
                proxy_method_wrapper(
                    attrname,
                    self._generic_mixin_proxy_methods__link_field))

        return res
