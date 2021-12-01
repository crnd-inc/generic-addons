import binascii
import logging
from odoo import models, fields, api, exceptions, tools, _

try:
    from cryptography.fernet import Fernet
except (ImportError, IOError):
    logging.getLogger(__name__).warning(
        "Cannot import Fernet from cryptography")


class GenericCryptoParam(models.Model):
    """ Model to store encrypted configuration parameters.
        The only reason for this model is to avoid storing some configuration
        parameters in database in plain text.
        Example of such data could be access tokens,
        passwords to external serivces, etc.

        The program interface for this model is similar to
        'ir.config_parameter'

        Currently it does not implement inmemory caching of encrypted params.
    """
    _name = 'generic.crypto.param'
    _description = 'Generic Crypto Param'

    key = fields.Char(index=True, required=True)
    value = fields.Text()

    _sql_constraints = [
        ('key_uniq', 'unique (key)', 'Param key must be unique.')
    ]

    def _get_ecnryption_context(self):
        if not tools.config.get('crypto_token', False):
            raise exceptions.UserError(_(
                "You must add 'crypto_token' to 'odoo.conf' to be able "
                "to use this feature"))
        try:
            fernet = Fernet(tools.config.get('crypto_token').encode('utf-8'))
        except (binascii.Error, ValueError):
            raise exceptions.UserError(_(
                "Invalid 'crypto_token'! "
                "Ensure it is valid 32-bytes base64-encoded string!"))
        except ImportError:
            raise exceptions.UserError(_(
                "It seems that python package 'cryptography' is not installed!"
                "Please, install "
                "[cryptography](https://pypi.org/project/cryptography/) "
                "package and try again"))
        return fernet

    def _encrypt_value(self, value):
        """ Encrypt value and return result

            :param str value: Value to encrypt
            :retrun str: encrypted value
        """
        fernet = self._get_ecnryption_context()
        return fernet.encrypt(value.encode('utf8'))

    @api.model
    def set_param(self, key, value):
        """ Set the crypto param 'key' to value 'value'
            Always return True
        """
        param = self.search([('key', '=', key)])

        if param and value:
            param.write({'value': self._encrypt_value(value)})
        elif param and not value:
            param.unlink()
        elif not param and value:
            self.create({
                'key': key,
                'value': self._encrypt_value(value)})
        return True

    @api.model
    def get_param(self, key, default=False):
        """ Return the value of crypto param 'key'
        """
        fernet = self._get_ecnryption_context()

        params = self.search_read(
            [('key', '=', key)],
            fields=['value'],
            limit=1)
        if params and params[0]['value']:
            return fernet.decrypt(
                params[0]['value'].encode('utf-8')
            ).decode("utf-8")
        return default
