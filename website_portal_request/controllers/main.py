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
        partner = request.env.user.partner_id
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
        #    page=page,
            step=self._items_per_page
        )

        # search the count to display, according to the pager data
        requests = Request.search(
            domain, limit=self._items_per_page, offset=pager['offset'])
        _logger.info("CREATE. requests: %s", requests)

        values.update({
            'requests': requests,
            'pager': pager,
#            'archive_groups': archive_groups,
            'default_url': '/my/requests',
        })

        _logger.info("CREATE. VALUE: %s", values)

        # values.update({
        #     'requests': Request.search([])
        # })
        return request.website.render('website_portal_request.portal_my_request', values)

    @http.route(["/my/requests/<int:request_id>"], type='http',
           auth="user", website=True)
    def portal_my_req(self, request_id):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        Request = request.env['request.request']


        reques = Request.browse(request_id)

        values.update({
            'reques': reques,
        })

        return request.website.render(
            "website_portal_request.portal_request", values)


    # @http.route(['/my/quotes', '/my/quotes/page/<int:page>'], type='http',
    #             auth="user", website=True)
    # def portal_my_quotes(self, page=1, date_begin=None, date_end=None, **kw):
    #     values = self._prepare_portal_layout_values()
    #     partner = request.env.user.partner_id
    #     SaleOrder = request.env['sale.order']

    #     domain = [
    #         ('message_partner_ids', 'child_of',
    #          [partner.commercial_partner_id.id]),
    #         ('state', 'in', ['sent', 'cancel'])
    #     ]

    #     archive_groups = self._get_archive_groups('sale.order', domain)
    #     if date_begin and date_end:
    #         domain += [('create_date', '>=', date_begin),
    #                    ('create_date', '<', date_end)]

    #     # count for pager
    #     quotation_count = SaleOrder.search_count(domain)
    #     # make pager
    #     pager = request.website.pager(
    #         url="/my/quotes",
    #         url_args={'date_begin': date_begin, 'date_end': date_end},
    #         total=quotation_count,
    #         page=page,
    #         step=self._items_per_page
    #     )
    #     # search the count to display, according to the pager data
    #     quotations = SaleOrder.search(
    #         domain, limit=self._items_per_page, offset=pager['offset'])

    #     values.update({
    #         'date': date_begin,
    #         'quotations': quotations,
    #         'pager': pager,
    #         'archive_groups': archive_groups,
    #         'default_url': '/my/quotes',
    #     })
    #     return request.website.render(
    #         "website_portal_sale_v10.portal_my_quotations", values)


    # def account(self):
    #     """ Add sales documents to main account page """
    #     response = super(WebsiteAccount, self).account()
    #     partner = request.env.user.partner_id

    #     Request = request.env['request.request']
    #     request_count = Request.search_count([
    #         ('message_partner_ids', 'child_of',
    #          [partner.commercial_partner_id.id]),
    #         ('name', 'in', ['open', 'paid', 'cancelled'])
    #     ])

    #     response.qcontext.update({
    #         'request_count': request_count,
    #     })
    #     return response

    # @http.route(['/my/requests', '/my/requests/page/<int:page>'], type='http',
    #             auth="user", website=True)
    # def portal_my_requests(self, page=1, date_begin=None, date_end=None, **kw):
    #     values = self._prepare_portal_layout_values()
    #     partner = request.env.user.partner_id
    #     RequestPortal = request.env['request.request']

    #     domain = [
    #         ('message_partner_ids', 'child_of',
    #          [partner.commercial_partner_id.id]),
    #         ('state', 'in', ['open', 'paid', 'cancelled'])
    #     ]
    #     archive_groups = self._get_archive_groups('account.invoice', domain)
    #     if date_begin and date_end:
    #         domain += [('create_date', '>=', date_begin),
    #                    ('create_date', '<', date_end)]

    #     # count for pager
    #     request_count = RequestPortal.search_count(domain)
    #     # pager
    #     pager = request.website.pager(
    #         url="/my/requests",
    #         url_args={'date_begin': date_begin, 'date_end': date_end},
    #         total=request_count,
    #         page=page,
    #         step=self._items_per_page
    #     )
    #     # content according to pager and archive selected
    #     requests = RequestPortal.search(
    #         domain, limit=self._items_per_page, offset=pager['offset'])
    #     values.update({
    #         'date': date_begin,
    #         'invoices': invoices,
    #         'page_name': 'invoice',
    #         'pager': pager,
    #         'archive_groups': archive_groups,
    #         'default_url': '/my/invoices',
    #     })
    #     return request.website.render(
    #         "website_portal_request.portal_my_requests", values)
