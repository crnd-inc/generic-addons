def resource_proxy(method):
    """ Decorate resource methods, that have to be proxied to
        resource implementation models with this deocrator

        For example:

            @resource_proxy
            def action_view_resource_documents(self):
                pass

        Such methods will be available on resource implementation model.
        This is required to make stat-buttons work on both: resource and
        resource implementation
    """
    method.__resource_proxy__ = True
    return method
