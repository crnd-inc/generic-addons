import datetime
import math
from odoo.tools.float_utils import float_round


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


def float_to_time(hours):
    """ Convert a number of hours into a time object. """
    if hours == 24.0:
        return datetime.time.max
    fractional, integral = math.modf(hours)
    return datetime.time(
        int(integral),
        int(float_round(60 * fractional, precision_digits=0)), 0)
