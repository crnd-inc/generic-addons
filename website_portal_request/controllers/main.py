# -*- coding: utf-8 -*-

from openerp import http
from openerp.http import request
from openerp.addons.website_portal_v10.controllers.main import WebsiteAccount


class WebsiteAccount(WebsiteAccount):

    @http.route(['/my/requests'], type='http',
                auth="user", website=True)
    def portal_my_request(self, **kw):
        values = self._prepare_portal_layout_values()
        Request = request.env['request.request']
        domain = []
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
        values.update({
            'requests': requests,
            'pager': pager,
            'default_url': '/my/requests',
        })

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
