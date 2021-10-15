def ensure_code_or_name(code, name):
    """ Simple function that checks that at least core or name is not falsy
    """
    if not (bool(code) or bool(name)):
        raise AssertionError(
            "'code' or 'name' must not be None! (code=%s;name=%s)"
            "" % (code, name))
