# -*- coding: utf-8 -*-
from openerp import models


class RequestRequest(models.Model):
    _inherit = "request.request"
    _mail_post_access = 'read'

