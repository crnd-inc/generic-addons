from odoo import models, fields

from odoo.addons.generic_mixin import generate_proxy_decorator

proxy_method = generate_proxy_decorator('__proxy_base_record__')


class MyBaseModel(models.Model):
    _name = 'test.proxy.method.my.base.model'
    _inherit = [
        'generic.mixin.proxy.methods',
    ]
    _description = "Test Generic Mixin: Proxy method my base model"

    _generic_mixin_proxy_methods__dest_model = (
        'test.proxy.method.my.specific.model.mixin')
    _generic_mixin_proxy_methods__link_field = 'base_record_id'
    _generic_mixin_proxy_methods__method_attr = (
        '__proxy_base_record__')

    base_field = fields.Char()

    @proxy_method
    def action_my_action(self):
        for record in self:
            record.base_field = 'action-done'

    @proxy_method
    def action_my_action_multi(self):
        for record in self:
            record.base_field = 'action-done-%s' % record.base_field


class MySpecificModelMixin(models.AbstractModel):
    _name = 'test.proxy.method.my.specific.model.mixin'
    _description = "Test Generic Mixin: Proxy method my specific model mixin"

    base_record_id = fields.Many2one(
        'test.proxy.method.my.base.model', delegate=True, required=True,
        ondelete='cascade', readonly=True)


class MySpecificModel1(models.Model):
    _name = 'test.proxy.method.my.specific.model.1'
    _inherit = 'test.proxy.method.my.specific.model.mixin'
    _description = "Test Generic Mixin: Proxy method my specific model 1"

    specific_field_1 = fields.Char()


class MySpecificModel2(models.Model):
    _name = 'test.proxy.method.my.specific.model.2'
    _inherit = 'test.proxy.method.my.specific.model.mixin'
    _description = "Test Generic Mixin: Proxy method my specific model 1"

    specific_field_2 = fields.Char()
