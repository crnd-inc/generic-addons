from openerp.tools import config

import logging
_logger = logging.getLogger(__name__)

# This model is required only for tests.
if config.get('test_enable', False):
    from openerp import models, fields
    _logger.info("Create test model")

    class TestModel(models.Model):
        _name = 'generic.tag.test.model'
        _inherit = [
            'generic.tag.mixin'
        ]

        name = fields.Char('Name')
        test_field = fields.Char('test_field')












