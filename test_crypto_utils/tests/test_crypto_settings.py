from odoo.tests.common import SavepointCase
from odoo.tools import config


class TestCryptoSettings(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestCryptoSettings, cls).setUpClass()

        cls.old_token = config.options.get('crypto_token', None)
        config['crypto_token'] = 'EOjtljxNLRoalHgfIb7LIg0jg0iUQLOZLnuGx8zXPC0='

    @classmethod
    def tearDownClass(cls):
        super(TestCryptoSettings, cls).setUpClass()

        config['crypto_token'] = cls.old_token

    def _search_param(self, key):
        return  self.env['generic.crypto.param'].search(
            [('key', '=', key)], limit=1)

    def test_crypto_settings(self):
        value = 'Super secred param'
        key = 'my.super.secret.42'

        # No param with such key
        self.assertFalse(self._search_param(key))

        # Default value is placeholder
        config_default = self.env['res.config.settings'].default_get(
            list(self.env['res.config.settings']._fields.keys())
        )
        self.assertEqual(config_default['my_super_secret_42'], '******')

        # Save config without no changes
        config = self.env['res.config.settings'].create(config_default)
        config.execute()

        # Parameter is not set
        self.assertFalse(self._search_param(key))

        # Save with updated secret
        config = self.env['res.config.settings'].create(dict(
            config_default,
            my_super_secret_42='secret-42',
        ))
        config.execute()

        # Check that parma was saved
        self.assertTrue(self._search_param(key))
        self.assertEqual(
            self.env['generic.crypto.param'].get_param(key),
            'secret-42')

        # Ensure that wizard will still show placeholder instead of value
        config_default = self.env['res.config.settings'].default_get(
            list(self.env['res.config.settings']._fields.keys())
        )
        self.assertEqual(config_default['my_super_secret_42'], '******')

        # Try to unset param
        config = self.env['res.config.settings'].create(dict(
            config_default,
            my_super_secret_42='',
        ))
        config.execute()

        # Ensure param was unset
        self.assertFalse(self._search_param(key))
        self.assertFalse(self.env['generic.crypto.param'].get_param(key))
