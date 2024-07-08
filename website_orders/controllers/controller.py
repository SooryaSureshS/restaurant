from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.backend import WebsiteSaleBackend
from odoo import fields, http, _
from datetime import datetime, timedelta, time
import babel.dates
from odoo.tools.misc import get_lang


class websiteBackend(http.Controller):
    @http.route('/website/fetch_dashboard_data', type="json", auth='user')
    def fetch_dashboard_data(self, website_id, date_from, date_to):
        Website = request.env['website']
        has_group_system = request.env.user.has_group('base.group_system')
        has_group_designer = request.env.user.has_group('website.group_website_designer')
        dashboard_data = {
            'groups': {
                'system': has_group_system,
                'website_designer': has_group_designer
            },
            'currency': request.env.company.currency_id.id,
            'dashboards': {
                'visits': {},
            }
        }

        current_website = website_id and Website.browse(website_id) or Website.get_current_website()
        multi_website = request.env.user.has_group('website.group_multi_website')
        websites = multi_website and request.env['website'].search([]) or current_website
        dashboard_data['websites'] = websites.read(['id', 'name'])
        for rec, website in zip(websites, dashboard_data['websites']):
            website['domain'] = rec._get_http_domain()
            if website['id'] == current_website.id:
                website['selected'] = True

        if has_group_designer:
            if current_website.google_management_client_id and current_website.google_analytics_key:
                dashboard_data['dashboards']['visits'] = dict(
                    ga_client_id=current_website.google_management_client_id or '',
                    ga_analytics_key=current_website.google_analytics_key or '',
                )
        results=dashboard_data
        date_date_from = fields.Date.from_string(date_from)
        date_date_to = fields.Date.from_string(date_to)
        date_diff_days = (date_date_to - date_date_from).days
        datetime_from = datetime.combine(date_date_from, time.min)
        datetime_to = datetime.combine(date_date_to, time.max)

        sales_values = dict(
            graph=[],
            best_sellers=[],
            summary=dict(
                order_count=0, order_carts_count=0, order_unpaid_count=0,
                order_to_invoice_count=0, order_carts_abandoned_count=0,
                payment_to_capture_count=0, total_sold=0,
                order_per_day_ratio=0, order_sold_ratio=0, order_convertion_pctg=0,
            )
        )

        results['dashboards']['sales'] = sales_values

        results['groups']['sale_salesman'] = request.env['res.users'].has_group('sales_team.group_sale_salesman')

        if not results['groups']['sale_salesman']:
            return results

        results['dashboards']['sales']['utm_graph'] = self.fetch_utm_data(datetime_from, datetime_to)
        # Product-based computation
        sale_report_domain = [
            ('website_id', '=', current_website.id),
            ('state', 'in', ['sale', 'done']),
            ('date', '>=', datetime_from),
            ('date', '<=', fields.Datetime.now())
        ]
        report_product_lines = request.env['sale.report'].read_group(
            domain=sale_report_domain,
            fields=['product_tmpl_id', 'product_uom_qty', 'price_subtotal'],
            groupby='product_tmpl_id', orderby='product_uom_qty desc', limit=5)

        for product_line in report_product_lines:

            if product_line['product_tmpl_id'] != False:
                product_tmpl_id = request.env['product.template'].browse(product_line['product_tmpl_id'][0])
                sales_values['best_sellers'].append({
                    'id': product_tmpl_id.id,
                    'name': product_tmpl_id.name,
                    'qty': product_line['product_uom_qty'],
                    'sales': product_line['price_subtotal'],
                })

        # Sale-based results computation
        sale_order_domain = [
            ('website_id', '=', current_website.id),
            ('date_order', '>=', fields.Datetime.to_string(datetime_from)),
            ('date_order', '<=', fields.Datetime.to_string(datetime_to))]
        so_group_data = request.env['sale.order'].read_group(sale_order_domain, fields=['state'], groupby='state')
        for res in so_group_data:
            if res.get('state') == 'sent':
                sales_values['summary']['order_unpaid_count'] += res['state_count']
            elif res.get('state') in ['sale', 'done']:
                sales_values['summary']['order_count'] += res['state_count']
            sales_values['summary']['order_carts_count'] += res['state_count']

        report_price_lines = request.env['sale.report'].read_group(
            domain=[
                ('website_id', '=', current_website.id),
                ('state', 'in', ['sale', 'done']),
                ('date', '>=', datetime_from),
                ('date', '<=', datetime_to)],
            fields=['team_id', 'price_subtotal'],
            groupby=['team_id'],
        )
        sales_values['summary'].update(
            order_to_invoice_count=request.env['sale.order'].search_count(sale_order_domain + [
                ('state', 'in', ['sale', 'done']),
                ('order_line', '!=', False),
                ('partner_id', '!=', request.env.ref('base.public_partner').id),
                ('invoice_status', '=', 'to invoice'),
            ]),
            order_carts_abandoned_count=request.env['sale.order'].search_count(sale_order_domain + [
                ('is_abandoned_cart', '=', True),
                ('cart_recovery_email_sent', '=', False)
            ]),
            payment_to_capture_count=request.env['payment.transaction'].search_count([
                ('state', '=', 'authorized'),
                # that part perform a search on sale.order in order to comply with access rights as tx do not have any
                ('sale_order_ids', 'in',
                 request.env['sale.order'].search(sale_order_domain + [('state', '!=', 'cancel')]).ids),
            ]),
            total_sold=sum(price_line['price_subtotal'] for price_line in report_price_lines)
        )

        # Ratio computation
        sales_values['summary']['order_per_day_ratio'] = round(
            float(sales_values['summary']['order_count']) / date_diff_days, 2)
        sales_values['summary']['order_sold_ratio'] = round(
            float(sales_values['summary']['total_sold']) / sales_values['summary']['order_count'], 2) if \
            sales_values['summary']['order_count'] else 0
        sales_values['summary']['order_convertion_pctg'] = 100.0 * sales_values['summary']['order_count'] / \
                                                           sales_values['summary']['order_carts_count'] if \
            sales_values['summary']['order_carts_count'] else 0

        # Graphes computation
        if date_diff_days == 7:
            previous_sale_label = _('Previous Week')
        elif date_diff_days > 7 and date_diff_days <= 31:
            previous_sale_label = _('Previous Month')
        else:
            previous_sale_label = _('Previous Year')

        sales_values['graph'] += [{
            'values': self._compute_sale_graph(date_date_from, date_date_to, sale_report_domain),
            'key': 'Untaxed Total',
        }, {
            'values': self._compute_sale_graph(date_date_from - timedelta(days=date_diff_days), date_date_from,
                                               sale_report_domain, previous=True),
            'key': previous_sale_label,
        }]

        return results

# class WebsiteSaleBackend1(WebsiteSaleBackend):
#
#     @http.route()
#     def fetch_dashboard_data(self, website_id, date_from, date_to):
#         Website = request.env['website']
#         current_website = website_id and Website.browse(website_id) or Website.get_current_website()
#
#         results = super(WebsiteSaleBackend1, self).fetch_dashboard_data(website_id, date_from, date_to)
#
#         date_date_from = fields.Date.from_string(date_from)
#         date_date_to = fields.Date.from_string(date_to)
#         date_diff_days = (date_date_to - date_date_from).days
#         datetime_from = datetime.combine(date_date_from, time.min)
#         datetime_to = datetime.combine(date_date_to, time.max)
#
#         sales_values = dict(
#             graph=[],
#             best_sellers=[],
#             summary=dict(
#                 order_count=0, order_carts_count=0, order_unpaid_count=0,
#                 order_to_invoice_count=0, order_carts_abandoned_count=0,
#                 payment_to_capture_count=0, total_sold=0,
#                 order_per_day_ratio=0, order_sold_ratio=0, order_convertion_pctg=0,
#             )
#         )
#
#         results['dashboards']['sales'] = sales_values
#
#         results['groups']['sale_salesman'] = request.env['res.users'].has_group('sales_team.group_sale_salesman')
#
#         if not results['groups']['sale_salesman']:
#             return results
#
#         results['dashboards']['sales']['utm_graph'] = self.fetch_utm_data(datetime_from, datetime_to)
#         # Product-based computation
#         sale_report_domain = [
#             ('website_id', '=', current_website.id),
#             ('state', 'in', ['sale', 'done']),
#             ('date', '>=', datetime_from),
#             ('date', '<=', fields.Datetime.now())
#         ]
#         report_product_lines = request.env['sale.report'].read_group(
#             domain=sale_report_domain,
#             fields=['product_tmpl_id', 'product_uom_qty', 'price_subtotal'],
#             groupby='product_tmpl_id', orderby='product_uom_qty desc', limit=5)
#
#         for product_line in report_product_lines:
#
#             if product_line['product_tmpl_id'] != False:
#                 product_tmpl_id = request.env['product.template'].browse(product_line['product_tmpl_id'][0])
#                 sales_values['best_sellers'].append({
#                     'id': product_tmpl_id.id,
#                     'name': product_tmpl_id.name,
#                     'qty': product_line['product_uom_qty'],
#                     'sales': product_line['price_subtotal'],
#                 })
#
#         # Sale-based results computation
#         sale_order_domain = [
#             ('website_id', '=', current_website.id),
#             ('date_order', '>=', fields.Datetime.to_string(datetime_from)),
#             ('date_order', '<=', fields.Datetime.to_string(datetime_to))]
#         so_group_data = request.env['sale.order'].read_group(sale_order_domain, fields=['state'], groupby='state')
#         for res in so_group_data:
#             if res.get('state') == 'sent':
#                 sales_values['summary']['order_unpaid_count'] += res['state_count']
#             elif res.get('state') in ['sale', 'done']:
#                 sales_values['summary']['order_count'] += res['state_count']
#             sales_values['summary']['order_carts_count'] += res['state_count']
#
#         report_price_lines = request.env['sale.report'].read_group(
#             domain=[
#                 ('website_id', '=', current_website.id),
#                 ('state', 'in', ['sale', 'done']),
#                 ('date', '>=', datetime_from),
#                 ('date', '<=', datetime_to)],
#             fields=['team_id', 'price_subtotal'],
#             groupby=['team_id'],
#         )
#         sales_values['summary'].update(
#             order_to_invoice_count=request.env['sale.order'].search_count(sale_order_domain + [
#                 ('state', 'in', ['sale', 'done']),
#                 ('order_line', '!=', False),
#                 ('partner_id', '!=', request.env.ref('base.public_partner').id),
#                 ('invoice_status', '=', 'to invoice'),
#             ]),
#             order_carts_abandoned_count=request.env['sale.order'].search_count(sale_order_domain + [
#                 ('is_abandoned_cart', '=', True),
#                 ('cart_recovery_email_sent', '=', False)
#             ]),
#             payment_to_capture_count=request.env['payment.transaction'].search_count([
#                 ('state', '=', 'authorized'),
#                 # that part perform a search on sale.order in order to comply with access rights as tx do not have any
#                 ('sale_order_ids', 'in',
#                  request.env['sale.order'].search(sale_order_domain + [('state', '!=', 'cancel')]).ids),
#             ]),
#             total_sold=sum(price_line['price_subtotal'] for price_line in report_price_lines)
#         )
#
#         # Ratio computation
#         sales_values['summary']['order_per_day_ratio'] = round(
#             float(sales_values['summary']['order_count']) / date_diff_days, 2)
#         sales_values['summary']['order_sold_ratio'] = round(
#             float(sales_values['summary']['total_sold']) / sales_values['summary']['order_count'], 2) if \
#         sales_values['summary']['order_count'] else 0
#         sales_values['summary']['order_convertion_pctg'] = 100.0 * sales_values['summary']['order_count'] / \
#                                                            sales_values['summary']['order_carts_count'] if \
#         sales_values['summary']['order_carts_count'] else 0
#
#         # Graphes computation
#         if date_diff_days == 7:
#             previous_sale_label = _('Previous Week')
#         elif date_diff_days > 7 and date_diff_days <= 31:
#             previous_sale_label = _('Previous Month')
#         else:
#             previous_sale_label = _('Previous Year')
#
#         sales_values['graph'] += [{
#             'values': self._compute_sale_graph(date_date_from, date_date_to, sale_report_domain),
#             'key': 'Untaxed Total',
#         }, {
#             'values': self._compute_sale_graph(date_date_from - timedelta(days=date_diff_days), date_date_from,
#                                                sale_report_domain, previous=True),
#             'key': previous_sale_label,
#         }]
#
#         return results


class Website(http.Controller):

    @http.route('/order_history', type='http', auth='public', website=True)
    def navigate_to_detail_page(self):
        uid = request.session.uid
        if uid:
            employee = request.env['res.users'].sudo().search_read([('id', '=', uid)], limit=1)
            login_id = employee[0]['partner_id'][0]
            saleorderline = request.env['sale.order.line'].search([])
            saleorder = request.env['sale.order'].search([])
            order = {}
            orderlist = []
            flag = 0
            for so in saleorder:
                if so.partner_id.id == login_id:
                    for sol in saleorderline:
                        if so.id == sol.order_id.id:
                            if sol.product_uom_qty > 0:
                                order['Order_ID'] = so.id
                                order['Order'] = so.name
                                order['product'] = sol.product_id.name
                                order['Ordered_Quantity'] = sol.product_uom_qty
                                order['ids'] = sol.id
                                if sol.order_line_state == 'done':
                                    order['Delivery_Status'] = 'Delivered'
                                elif sol.order_line_state == 'preparing':
                                    order['Delivery_Status'] = 'Preparing'
                                elif sol.order_line_state == 'waiting':
                                    order['Delivery_Status'] = 'Waiting'
                                elif     sol.order_line_state == 'delivering':
                                    order['Delivery_Status'] = 'Out for Delivery'
                                elif sol.order_line_state == 'cancel':
                                    order['Delivery_Status'] = 'Cancelled'
                                elif sol.order_line_state == 'return':
                                    order['Delivery_Status'] = 'Returned'
                                flag = 1
                    if flag == 1:
                        orderlist.append(order)
                        order = {}
                        flag = 0
            orders = {"orderlist": orderlist}
            return request.render('website_orders.order_history', orders)
        else:
            return request.redirect('/web/login')

    @http.route(['/cancel/<page>'], type='http', auth="public", website=True, csrf=False, sitemap=False)
    def cancel_order_line(self, **post):
        line = post["page"]

        line = request.env['sale.order.line'].sudo().search([('id', '=', line)])
        if line:
            line.write({'order_line_state': 'cancel'})

        return request.redirect('/order_history')

# @http.route(['/return/<page>'], type='http', auth="public", website=True, csrf=False, sitemap=False)
#  def return_order_line(self, **post):
#    line = post["page"]

#     line = request.env['sale.order.line'].sudo().search([('id', '=', line)])
#    if line:
#       line.write({'order_line_state': 'return'})
#
#
#    return request.redirect('/order_history')
