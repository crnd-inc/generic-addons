# -*- coding: utf-8 -*-
import io
from PIL import Image
import json
import collections

from openerp.addons.web.controllers.main import Home
from openerp import http
from openerp import tools
from openerp import _
from openerp.exceptions import ValidationError
from openerp.tools import ustr
from openerp.http import request

import logging
_logger = logging.getLogger(__name__)


class WebsitePortalHelpers(Home):

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
            except IOError as e:
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

    @http.route('/website_portal_request/api/categories', type='json',
                auth='user', methods=['POST'])
    def public_categories(self, **post_data):
        RequestCategory = request.env['request.category'].sudo()

        public_categories = RequestCategory.search([
            ('website_published', '=', True)
        ])
        res = []
        for category in public_categories:
            res.append({
                'name': category.name,
                'code': category.code,
                'display_name': category.display_name,
                'id': category.id,
            })
        return res

    @http.route('/website_portal_request/api/category/types',
                type='json', auth='user', methods=['POST'])
    def public_category_types(self, category_id, **post_data):
        RequestCategory = request.env['request.category'].sudo()
        RequestType = request.env['request.type'].sudo()

        category = RequestCategory.search([
            ('id', '=', category_id),
            ('website_published', '=', True),
        ], limit=1)
        if not category:
            raise request.not_found()

        public_types = RequestType.search([
            ('category_id', '=', category.id),
            ('website_published', '=', True),
        ])

        res = []
        for request_type in public_types:
            res.append({
                'name': request_type.name,
                'code': request_type.code,
                'id': request_type.id,
            })
        return res

    @http.route('/website_portal_request/api/type_info',
                type='json', auth='user', methods=['POST'])
    def get_request_type_info(self, type_id, **post_data):
        RequestType = request.env['request.type'].sudo()

        request_type = RequestType.search([
            ('id', '=', type_id),
            ('website_published', '=', True),
        ], limit=1)
        if not request_type:
            raise request.not_found()
        return {
            'name': request_type.name,
            'code': request_type.code,
            'help': request_type.help_html,
            'id': request_type.id,
        }

    @http.route('/website_portal_request/api/request/new',
                type='json', auth='user', methods=['POST'])
    def create_request(self, type_id, request_text, **post_data):
        RequestType = request.env['request.type'].sudo()
        RequestRequest = request.env['request.request']

        request_type = RequestType.search([
            ('id', '=', type_id),
            ('website_published', '=', True),
        ], limit=1)
        if not request_type:
            raise ValidationError(_("Request type not found"))

        RequestRequest.check_access_rights('create')
        RequestRequest.check_access_rule('create')

        req = RequestRequest.create({
            'type_id': request_type.id,
            'request_text': request_text,
        })
        return {
            'id': req.id,
            'url': '/my/requests/%d' % req.id,
        }
