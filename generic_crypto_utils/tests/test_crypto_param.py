from odoo.tests.common import SavepointCase
from odoo.tools import config


class TestCryptoParam(SavepointCase):

    def test_crypto_param(self):
        old_token = config.options.get('crypto_token', None)
        config['crypto_token'] = (  # nosec
            'EOjtljxNLRoalHgfIb7LIg0jg0iUQLOZLnuGx8zXPC0=')
        value = 'Super secred param'

        gval = self.env['generic.crypto.param'].get_param('my.value')
        self.assertFalse(gval)

        self.env['generic.crypto.param'].set_param('my.value', value)

        gval = self.env['generic.crypto.param'].get_param('my.value')
        self.assertIsInstance(gval, str)
        self.assertEqual(gval, value)

        xval = self.env['generic.crypto.param'].search(
            [('key', '=', 'my.value')], limit=1).value
        self.assertIsInstance(xval, str)
        self.assertNotEqual(xval, value)

        config['crypto_token'] = old_token
