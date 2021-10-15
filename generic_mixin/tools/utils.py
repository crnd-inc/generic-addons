def removeprefix(s, prefix):
    """ Remove prefix from the string.
        Return copy of the string without prefix.
    """
    if s.startswith(prefix):
        return s[len(prefix):]
    return s


def removesuffix(s, suffix):
    """ Remove suffix from the string.
        Return copy of the string without suffix.
    """
    if s.endswith(suffix):
        return s[:-len(suffix)]
    return s
