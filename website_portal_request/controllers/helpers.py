# -*- coding: utf-8 -*-
import io
from PIL import Image
import json

from openerp.addons.web.controllers.main import Home
from openerp import http
from openerp import tools
from openerp import _
from openerp.tools import ustr
from openerp.http import request

import logging
_logger = logging.getLogger(__name__)


class WebsiteAttachment(Home):

    # Following code is based on odoo's /web_editor/attachment/add handler
    @http.route('/website_portal_request/image_upload', type='http',
                auth='user', methods=['POST'])
    def attach(self, upload, disable_optimization=False, **post_data):
        Attachments = request.env['ir.attachment']

        try:
            data = upload.read()

            try:
                image = Image.open(io.BytesIO(data))
                w, h = image.size
                if w * h >= 42e6:  # Nokia Lumia 1020 photo resolution
                    raise ValueError(_(
                        u"Image size excessive, uploaded images "
                        u"must be smaller than 42 million pixel"))
                if not disable_optimization and image.format in ('PNG',
                                                                 'JPEG'):
                    data = tools.image_save_for_web(image)
            except IOError, e:
                pass

            if post_data.get('context', False):
                Attachments = Attachments.with_context(
                    post_data.get('context', {}))

            attachment = Attachments.create({
                'name': 'Image',
                'datas': data.encode('base64'),
                'datas_fname': 'image',
                'public': True,
                # 'res_model': 'ir.ui.view',
            })
            res = {
                'status': 'OK',
                'attachment_url': "/web/image/%d" % attachment.id,
            }
        except Exception as e:
            _logger.exception("Failed to upload image to attachment")
            message = ustr(e)
            res = {
                'status': 'FAIL',
                'message': message,
            }

        return json.dumps(res)
