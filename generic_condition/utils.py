# -*- coding: utf-8 -*-

import datetime

from openerp.tools import (DEFAULT_SERVER_DATETIME_FORMAT,
                           DEFAULT_SERVER_DATE_FORMAT)


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
        return datetime.datetime.strptime(
            value, DEFAULT_SERVER_DATETIME_FORMAT)

    if ttype == 'date':
        return datetime.datetime.strptime(
            value, DEFAULT_SERVER_DATE_FORMAT)
