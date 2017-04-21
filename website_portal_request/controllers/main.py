# -*- coding: utf-8 -*-

from openerp import http
from openerp.http import request

from openerp.addons.website_portal_v10.controllers.main import WebsiteAccount

import logging
_logger = logging.getLogger(__name__)


class WebsiteAccount(WebsiteAccount):

    # @http.route()
    # def account(self):
    #     """ Add sales documents to main account page """
    #     response = super(WebsiteAccount, self).account()
    #     partner = request.env.user.partner_id

    #     Request = request.env['sale.order']
    #     request_count = Request.search_count([
    #         ('message_partner_ids', 'child_of',
    #          [partner.commercial_partner_id.id]),
    #         ('state', 'in', ['sale', 'done'])
    #     ])

    #     response.qcontext.update({
    #         'request_count': request_count,
    #     })
    #     return response

    @http.route(['/my/requests'], type='http',
                auth="user", website=True)
    def portal_my_request(self, **kw):
        values = self._prepare_portal_layout_values()
        Request = request.env['request.request']
        domain = []
        # archive_groups = self._get_archive_groups('request.request', domain)
        # if date_begin and date_end:
        #     domain += [('create_date', '>=', date_begin),
        #                ('create_date', '<', date_end)]

        # count for pager
        request_count = Request.search_count(domain)
        # make pager
        pager = request.website.pager(
            url="/my/requests",
            total=request_count,
            step=self._items_per_page
        )

        # search the count to display, according to the pager data
        requests = Request.search(
            domain, limit=self._items_per_page, offset=pager['offset'])
        _logger.info("CREATE. requests: %s", requests)

        values.update({
            'requests': requests,
            'pager': pager,
            'default_url': '/my/requests',
        })

        _logger.info("CREATE. VALUE: %s", values)

        # values.update({
        #     'requests': Request.search([])
        # })
        return request.website.render(
            'website_portal_request.portal_my_request', values)

    @http.route(["/my/requests/<int:request_id>"], type='http',
                auth="user", website=True)
    def portal_my_req(self, request_id):
        values = self._prepare_portal_layout_values()
        Request = request.env['request.request']
        reques = Request.browse(request_id)
        values.update({
            'reques': reques,
        })

        return request.website.render(
            "website_portal_request.portal_request", values)
