from odoo.tests.common import SavepointCase
from odoo.tools import config


class TestCryptoParam(SavepointCase):

    def test_crypto_param(self):
        old_token = config.options.get('crypto_token', None)
        config.option.update({
            'crypto_token': 'EOjtljxNLRoalHgfIb7LIg0jg0iUQLOZLnuGx8zXPC0='
        })
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

        if old_token is None:
            config.option.pop('crypto_token', None)
        else:
            config.option.update({
                'crypto_token': old_token,
            })
