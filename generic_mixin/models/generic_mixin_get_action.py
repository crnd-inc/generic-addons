from odoo import models, api


class GenericMixinGetAction(models.AbstractModel):
    """ This mixin provides method to read odoo action and optionaly
        replace context and domain of that action in result.

        Usage (if current model inherits from this mixin):

        def action_my_action(self):
            return self.get_action_by_xmlid(
                'my_action_xml_id',
                domain=[my domain],
                context=[my context],
            )


        Usage (if current model does not inherits from this mixin):

        def action_my_action(self):
            return self.env['generic.mixin.get.action'].get_action_by_xmlid(
                'my_action_xml_id',
                domain=[my domain],
                context=[my context],
            )

    """
    _name = 'generic.mixin.get.action'
    _description = "Generic Mixin: Get Action"
    # Note: this mixin is developed primaraly for compatability with 14.0

    @api.model
    def get_action_by_xmlid(self, xmlid, context=None, domain=None,
                            name=None):
        """ Simple method to get action by xmlid and update resulting dict with
            provided "update_data".

            In Odoo 14, the regular users have no access to ir.actions.*
            models, so, this method could be used to read action, and modify
            context and domain of resulting dict.

            :param str xmlid: XML (external) ID of action ir.actions.* to read
            :param dict context: apply new context for action
            :param list domain: apply new domain for action
            :param str name: apply new name for action
                (also changes display name)
            :return dict: Data for specified action
        """
        action = self.env['ir.actions.actions']._for_xml_id(xmlid)
        if context is not None:
            action['context'] = context
        if domain is not None:
            action['domain'] = domain
        if name is not None:
            action['name'] = name
            action['display_name'] = name

        return action

    @api.model
    def get_form_action_by_xmlid(self, xmlid, context=None,
                                 res_id=0, name=None):
        """ Return action based on provided xmlid, that will open form view.
            Usually, this method could be used in cases, when it is needed
            to open form view to create new object for user or edit object.

            :param str xmlid: XML (external) ID of action ir.actions.* to read
            :param dict context: apply new context for action
            :param int res_id: ID of record to open form for edition.
                 By default, form will be opened for creation of new record.
            :param str name: apply new name for action
                (also changes display name)
            :return dict: Data for specified action
        """
        action = self.get_action_by_xmlid(xmlid, context=context, name=name)

        # Find form view from action:
        form_view = None
        for view_id, view_mode in action['views']:
            if view_mode == 'form':
                form_view = (view_id, view_mode)
                break
        if not form_view:
            form_view = (False, 'form')

        action['view_mode'] = 'form'
        action['views'] = [form_view]
        action['res_id'] = res_id
        return action
