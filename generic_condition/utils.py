import datetime
import odoo


def str_to_datetime(ttype, value):
    """ Convert string with Odoo's date/datetime to `datetime` object
        if value evaluates to False, then None will be returned

        :param str ttype: date type. Possible values: 'date' or 'datetime'
        :return: datetime.datetime instance
        :rtype: datetime.datetime
    """
    if not value:
        return None

    if ttype == 'datetime':
        return odoo.fields.Datetime.from_string(value)

    if ttype == 'date':
        return datetime.datetime.combine(
            odoo.fields.Date.from_string(value),
            datetime.datetime.min.time())
    return None
