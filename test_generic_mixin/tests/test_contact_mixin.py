import logging

from odoo.tests.common import TransactionCase, Form
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ContactMixinTest(TransactionCase):

    def test_website_link_sanitizer(self):
        Model = self.env['test.contact.mixin']

        # Test sanitizer on create record
        test_record = Model.create({
            'name': 'Test website link sanitizer',
            'website_link': 'create_test.com'
        })
        self.assertEqual(test_record.website_link, 'http://create_test.com')

        # Test sanitizer on write record
        test_record.write({
            'website_link': 'write_test.com'
        })
        self.assertEqual(test_record.website_link, 'http://write_test.com')

        test_record.write({
            'website_link': 'http://write_test_http.com'
        })
        self.assertEqual(
            test_record.website_link, 'http://write_test_http.com')

        test_record.write({
            'website_link': 'https://write_test_https.com'
        })
        self.assertEqual(
            test_record.website_link, 'https://write_test_https.com')

    def test_mail_link_sanitizer(self):
        Model = self.env['test.contact.mixin']

        with Form(Model) as fmodel:
            with self.assertRaises(UserError):
                fmodel.email = 'wrong_email'
                fmodel.save()
            with self.assertRaises(UserError):
                fmodel.email = '@wrong_email'
                fmodel.save()
            with self.assertRaises(UserError):
                fmodel.email = 'sdfsd@wrong_email'
                fmodel.save()
            fmodel.email = 'admin@admin.com'
            fmodel.save()
        self.assertEqual(fmodel.email, 'admin@admin.com')

    def test_mail_link_sanitizer(self):
        Model = self.env['test.contact.mixin']

        with Form(Model) as fmodel:
            with self.assertRaises(UserError):
                fmodel.link_telegram = 'http://UserLogin'
                fmodel.save()
            with self.assertRaises(UserError):
                fmodel.link_telegram = 'http://t.me/UserLogin'
                fmodel.save()
            fmodel.link_telegram = 'https://t.me/UserLogin'
            fmodel.save()
        self.assertEqual(fmodel.email, 'https://t.me/UserLogin')
