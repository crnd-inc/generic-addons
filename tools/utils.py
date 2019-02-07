def resource_proxy(method):
    method.__resource_proxy__ = True
    return method
