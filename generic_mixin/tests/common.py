import logging
import unittest
from odoo.tools.misc import mute_logger
from odoo.tools.sql import table_kind
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


def deactivate_records_for_model(env, model):
    """ Deactivate records from uninstalled modules for specified model.

        This could be used to deactivate ir.rules
        from unknown (at moment of test) modules.

        Or it could be used to deactivate menus that references actions
        for unexisting (not registered yet) models.
    """
    record_ids = env['ir.model.data'].search([
        ('model', '=', model),
        ('module', 'not in', tuple(env.registry._init_modules)),
    ]).mapped('res_id')
    env[model].browse(record_ids).write({'active': False})


class FindNew:
    """
        This context manager should simplify the search for new records
        that where created during event handling.

        An example of a simple search for the required record:

            old_records = self.env['my.model'].search([])

            # Do some work

            new_records = self.env['my.model'].search(
                [('id', 'not in', old_records.ids)])

            self.assertEqual(len(new_records), 1)

        Example using this context manager:

            with FindNew('my.model') as nr:
                # Do some work
            self.assertEqual(len(nr['my.model']), 1)

        Also, it is possible to handle new records in multiple models with
        single context manager:

            with FindNew('my.model.1', 'my.model.2') as nr:
                # Do some work
            self.assertEqual(len(nr['my.model.1'], 1)
            self.assertEqual(len(nr['my.model.2'], 4)
    """
    def __init__(self, env, *models):
        assert len(models) > 0, (  # nosec
            "At leas one model must be specified")
        self._env = env
        self._models = models
        self._main_model = models[0]
        self._records_map = {}
        for model in models:
            if table_kind(self._env.cr, self._env[model]._table) != 'r':
                raise TypeError('Only regular tables (models) allowed!')
            self._records_map[model] = self._env[model].browse()

    @property
    def main_model(self):
        """ The name of main model, used to determine new records
            via '.records' property

            :return str: name of model for 'records' property
        """
        return self._main_model

    @property
    def records(self):
        """ Return new records for main model.
            This property is kept only for backward compatibility

            :return: recordset with new records of main model
        """
        return self._records_map[self._main_model]

    @property
    def records_map(self):
        """ Return mapping that contains recordset with new records
            for each tracked model

            :return dict: mapping with recordsets with new records for each
                tracked model
        """
        return self._records_map

    def __getitem__(self, name):
        return self._records_map[name]

    def __enter__(self):
        self._search = {}
        for model in self._models:
            # TODO: Optimize this. Possibly it have sense to find max id
            #       and then search for new ids greater than max id
            self._search[model] = self._env[model].search([])
        return self

    def __exit__(self, etype, value, tracback):
        for model in self._models:
            self._records_map[model] = self._env[model].search(
                [('id', 'not in', self._search[model].ids)])


class ReduceLoggingMixin(unittest.TestCase):
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
    def run(self, result=None):
        return super(ReduceLoggingMixin, self).run(result=result)


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
        deactivate_records_for_model(cls.env, 'ir.rule')


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
        deactivate_records_for_model(self.env, 'ir.rule')


class WebTourCase(tests_common.HttpCase):

    def run_js_tour(self, start_url, tour_name, **kw):
        """ Run web tour.

            :param str start_url: Url to start web tour at
            :param str tour_name: Name of the tour to run
        """
        tour_service = "odoo.__DEBUG__.services['web_tour.tour']"
        js_run_tour = tour_service + ".run('%s')" % tour_name
        js_tour_ready = tour_service + ".tours.%s.ready" % tour_name
        ready_exp = "Boolean(%s && %s)" % (tour_service, js_tour_ready)
        return self.browser_js(
            url_path=start_url,
            code=js_run_tour,
            ready=kw.pop('ready', ready_exp),
            **kw)
