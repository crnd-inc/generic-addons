import logging
from odoo.tools.misc import mute_logger
from odoo.tools import config as tools_config
from odoo.tests import common as tests_common


# For compatability with 14.0
PORT = tools_config['http_port']
HOST = tests_common.HOST
TEST_URL = "http://%s:%s" % (HOST, PORT)


# pylint: disable=class-camelcase
class hide_log_messages:
    """ Temporary suppress log messages that pass fn_check

        Usage as decorator:

            @hide_log_messages(
                'odoo.tests',
                lambda r:
                    r.message.strip() == 'skip sending email in test mode')
            def my_method(self):
                pass

        Usage as context manager:

            def fn_filter(rec):
                msg = rec.message.strip()
                return msg == 'skip sending email in test mode'

            with hide_log_messages('odoo.test', fn_filter):
                pass

    """
    def __init__(self, logger, fn_check):
        self.logger = logger
        self.fn_check = fn_check

    def filter(self, record):
        return self.fn_check(record)

    def __enter__(self):
        logging.getLogger(self.logger).addFilter(self)

    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):
        logging.getLogger(self.logger).removeFilter(self)

    def __call__(self, func):
        import functools

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        return wrapper


class ReduceLoggingMixin:
    """ Simple mixin to remove boring messages from logging ourput.

        This class have to be mixed in test cases.
        As result, following messages will be filtered out from logging output:
            - odoo.tests (skip sending email in test mode)
            - odoo.models.unlink
            - odoo.addons.mail.models.mail_mail
    """

    @hide_log_messages(
        'odoo.tests',
        lambda r: r.message.strip() == 'skip sending email in test mode')
    @mute_logger(
        'odoo.models.unlink',
        'odoo.addons.mail.models.mail_mail')
    def run(self, *args, **kwargs):
        return super(ReduceLoggingMixin, self).run(*args, **kwargs)


class AccessRulesFixMixinST:
    """ Fix access rules for single transaction cases:
            - SingleTransactionCase
            - SavepointCase

        Deactivate rules created by modules that are not initialized to
        prevent errors raised when rule use field defined in uninitialized
        addon
    """

    @classmethod
    def setUpClass(cls):
        super(AccessRulesFixMixinST, cls).setUpClass()

        rule_ids = cls.env['ir.model.data'].search([
            ('model', '=', 'ir.rule'),
            ('module', 'not in', tuple(cls.env.registry._init_modules)),
        ]).mapped('res_id')
        cls.env['ir.rule'].browse(rule_ids).write({'active': False})


class AccessRulesFixMixinMT:
    """ Fix access rules for multi transaction cases
        - TransactionCase
        - HttpCase

        Deactivate rules created by modules that are not initialized to
        prevent errors raised when rule use field defined in uninitialized
        addon
    """

    def setUp(self):
        super(AccessRulesFixMixinMT, self).setUp()

        rule_ids = self.env['ir.model.data'].search([
            ('model', '=', 'ir.rule'),
            ('module', 'not in', tuple(self.env.registry._init_modules)),
        ]).mapped('res_id')
        self.env['ir.rule'].browse(rule_ids).write({'active': False})
