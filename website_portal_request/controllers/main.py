# -*- coding: utf-8 -*-

from openerp import http
from openerp.http import request
from openerp.addons.website_portal_v10.controllers.main import website_account


# NOTE: here is name collision with request, so be careful, when use name
# `request`. To avoid this name collision use names `req` and reqs` for
# `request.request` records


class WebsiteAccount(website_account):

    def _prepare_portal_layout_values(self):
        res = super(WebsiteAccount, self)._prepare_portal_layout_values()
        req_count = request.env['request.request'].search_count([])

        res.update({
            'req_count': req_count,
        })
        return res

    @http.route(['/my/requests'], type='http',
                auth="user", website=True)
    def portal_my_requests(self, **kw):
        values = self._prepare_portal_layout_values()
        domain = []
        # count for pager
        req_count = request.env['request.request'].search_count(domain)
        # make pager
        pager = request.website.pager(
            url="/my/requests",
            total=req_count,
            step=self._items_per_page
        )

        # search the count to display, according to the pager data
        reqs = request.env['request.request'].search(
            domain, limit=self._items_per_page, offset=pager['offset'])
        values.update({
            'reqs': reqs,
            'pager': pager,
            'default_url': '/my/requests',
        })

        return request.render(
            'website_portal_request.portal_my_requests', values)

    @http.route(["/my/requests/<int:req_id>"],
                type='http', auth="user", website=True)
    def portal_my_request(self, req_id, **kw):
        values = self._prepare_portal_layout_values()

        reqs = request.env['request.request'].search(
            [('id', '=', req_id)])

        if not reqs:
            raise request.not_found()

        reqs.check_access_rights('read')
        reqs.check_access_rule('read')

        values.update({
            'req': reqs,
        })
        return request.render(
            "website_portal_request.portal_my_request", values)
