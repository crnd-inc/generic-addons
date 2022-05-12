import functools


def monkey(obj, fn_name):
    """ Monkey patch object's fn_name attr

        For example:

            @monkey(server, 'start')
            def server_start(self, arg):
                res = server_start.__wrapped__(self, arg)
                # do some additional work
                return res
    """
    def monkey_wrapper(fn):
        orig = getattr(obj, fn_name)
        wrapper = functools.update_wrapper(fn, orig)
        setattr(obj, fn_name, wrapper)
        return wrapper
    return monkey_wrapper
