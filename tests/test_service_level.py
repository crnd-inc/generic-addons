import psycopg2
import logging

from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger

_logger = logging.getLogger(__name__)


class TestGenericServiceLevel(TransactionCase):

    def setUp(self):
        super(TestGenericServiceLevel, self).setUp()
        self.ServiceLevel = self.env['generic.service.level']
        self.demo_service_level_1 = self.env.ref(
            'generic_service.generic_service_level_1')

    @mute_logger('odoo.sql_db')
    def test_name_uniq_constraint(self):
        # Service level with name 'Level 1' and code 'level-1' - exists

        # test constraint name_uniq:
        with self.assertRaises(psycopg2.IntegrityError):
            self.ServiceLevel.create({
                'name': 'Level 1',
                'code': 'test',
            })

    @mute_logger('odoo.sql_db')
    def test_code_uniq_constraint(self):

        # test constraint code_uniq:
        with self.assertRaises(psycopg2.IntegrityError):
            self.ServiceLevel.create({
                'name': 'Test',
                'code': 'level-1',
            })

    @mute_logger('odoo.sql_db')
    def test_code_ascii_only_constraint(self):

        # test constraint code_ascii_only:
        with self.assertRaises(psycopg2.IntegrityError):
            self.ServiceLevel.create({
                'name': 'Test',
                'code': 'test!!#@{}',
            })

    def test_onchange_name_set_code(self):

        new_service_level = self.ServiceLevel.new({
            'name': 'Test!!#@{}__--Service//.<>,__True__Сервіс'
        })
        new_service_level._onchange_name_set_code()
        self.assertEqual(new_service_level.code, 'test-service-true-servis')
