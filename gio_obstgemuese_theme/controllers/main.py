# Company: giordano.ch AG
# Copyright by: giordano.ch AG
# https://giordano.ch/

import logging
import base64
import random
from odoo import fields, tools, _
from odoo import _, http, modules, _
from odoo.addons.website_sale.controllers.main import WebsiteSale, TableCompute
from odoo.addons.mass_mailing.controllers import main
from odoo.http import request, route
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website.models.ir_http import sitemap_qs2dom
from werkzeug.exceptions import NotFound

_logger = logging.getLogger(__name__)


class ObstMainHttpInherit(http.Controller):
    @http.route("/about", type="http", website=True, auth="public")
    def about_us_redirect(self):
        """
        about_us_redirect(self)

        Route: "/about"
        Access: Public
        Website: True

        This function retrieves the information of HR employees who are marked
        as 'is_website' and orders them based on the 'website_order' attribute.
        The retrieved data is then stored in a dictionary and passed as a value
         to the "gio_obstgemuese_theme.about_us_obst" template to render the
         about us page. The function returns the rendered template.
        """
        hr_employees = request.env['hr.employee'].sudo().search_read([
            ('is_website', '=', True)], order='website_order asc')
        val_dit = [{val: employee.get(val) for val in
                    ['id', 'name', 'job_title', 'website_order']}
                   for employee in hr_employees]
        val = {'employee_list': val_dit}
        return request.render("gio_obstgemuese_theme.about_us_obst", val)

    @http.route("/privacy", type="http", auth="public", website=True)
    def show_privacy_webpage(self, **kw):
        """
        show_privacy_webpage(self, **kw)

        Route: "/privacy"
        Access: Public
        Website: True

        This function renders the "gio_obstgemuese_theme.privacy_page" template
         and returns it. It takes in an optional argument 'kw' but it is not
          used in the function.
        """
        return request.render("gio_obstgemuese_theme.privacy_page", {})

    @http.route("/cookie/policy", type="json", auth="public", website=True)
    def obst_cookie_policy(self, **kw):
        """
        show_privacy_webpage(self, **kw)

        Route: "/privacy"
        Access: Public
        Website: True

        This function renders the "gio_obstgemuese_theme.privacy_page" template
         and returns it. It takes in an optional argument 'kw' but it is not
          used in the function.
        """
        return True if request.session.get('cookie') else 'No result'

    @http.route("/cookie/policy/accept", type="json", auth="public", website=True)
    def obst_cookie_policy_accept(self, **kw):
        """
        show_privacy_webpage(self, **kw)

        Route: "/privacy"
        Access: Public
        Website: True

        This function renders the "gio_obstgemuese_theme.privacy_page" template
         and returns it. It takes in an optional argument 'kw' but it is not
          used in the function.
        """
        request.session['cookie'] = True
        return True

    @http.route("/agb", type="http", auth="public", website=True)
    def show_agb_webpage(self, **kw):
        """
        show_privacy_webpage(self, **kw)

        Route: "/agb"
        Access: Public
        Website: True

        This function renders the "gio_obstgemuese_theme.agb_page" template and
         returns it. It takes in an optional argument 'kw' but it is not used
         in the function.
        """
        return request.render("gio_obstgemuese_theme.agb_page", {})

    @http.route("/search/products", type="http", auth="public", website=True)
    def products_search(self, search):
        """
        products_search(self, search)

        Route: "/search/products"
        Access: Public
        Website: True

        This function searches for product templates with a name that contains
        the value of the 'search' argument, which is case-insensitive.
        If there are any matches, the matched product templates are passed as
        a value to the "gio_obstgemuese_theme.product_search_page_template"
        template along with the 'has_product' and 'count' values. The function
        then returns the rendered template. If there is no match, the function
        returns the template with 'has_product' set to False.
        """
        product_template = request.env["product.template"].sudo()
        stories_obj = request.env['blog.post']
        vals = {}
        if search:
            stories = stories_obj.sudo().search([("name", "ilike", search), ('is_published', '=', True)])
            products = product_template.search(
                [("name", "ilike", search), ('sale_ok', '=', True), ('detailed_type', '=', 'product')])
            vals['product_list'] = products
            vals['story_list'] = stories
            vals['has_product'] = True if products else False
            vals['has_stories'] = True if stories else False
            vals['count'] = len(products)
        return request. \
            render("gio_obstgemuese_theme.product_search_page_template", vals)

    @http.route("/impressum", type="http", auth="public", website=True)
    def show_impressum_webpage(self, **kw):
        """
        show_impressum_webpage(self, **kw)

        Route: "/impressum"
        Access: Public
        Website: True

        This function renders the "gio_obstgemuese_theme.impressum_page"
        template and returns it. It takes in an optional argument 'kw'
        but it is not used in the function.
        """
        return http.request.render("gio_obstgemuese_theme.impressum_page", {})

    @http.route("/remove/order/line", type="json", auth="public", website=True)
    def remove_sale_order_line(self, line_id):
        """
        remove_sale_order_line(self, line_id)

        Route: "/remove/order/line"
        Access: Public
        Website: True

        This function removes a sale order line with the given line_id. It
        searches for the sale order line by its id, and if found, it unlinks it.
         Returns True if the order line is successfully unlinked, otherwise
          returns False.
        """
        sale_order_line = request.env["sale.order.line"].sudo()
        order_line = sale_order_line.search([("id", "=", int(line_id))])
        if order_line:
            order_line.unlink()
            return True
        else:
            return False

    @http.route("/get/cart/values", type="json", auth="public", website=True)
    def get_sale_cart(self):
        """
        This function returns information about the items in a user's cart in a JSON format.

        Route: "/get/cart/values"
        HTTP Type: JSON
        Auth: public
        Website: True

        Returns:
        {
        'cart_item': Boolean,
        'values': [{
        'product_name': str,
        'line_id': int,
        'product_img': str,
        'qty': float,
        'price': float,
        'symbol': str,
        'variant': dict,},...],
        'amount_total': float,}
        """
        order = request.website.sale_get_order()
        vals = []
        if not order.order_line:
            return {'cart_item': False}
        for line in order.order_line:
            variants = []
            val = {
                "product_name": line.product_id.name,
                "line_id": line.id,
                "product_img": line.product_id.image_1920,
                "qty": line.product_uom_qty,
                "price": line.price_unit,
                "symbol": line.currency_id.symbol,
            }
            variants = {prdt_attribute.display_name.split(':')[0]: prdt_attribute.display_name.split(':')[1] for
                        prdt_attribute in line.product_id.product_template_attribute_value_ids if prdt_attribute}
            val.update({"variant": variants})
            vals.append(val)
        return {'cart_item': True, 'values': vals, 'amount_total': order.amount_total}

    @http.route("/get/product/details", type="json", auth="public")
    def get_product_details(self, product_id):
        """
        Retrieve details of a product given its ID.

        Parameters:
        product_id (int): ID of the product to retrieve.

        Returns:
        dict: A dictionary containing the following keys:
        * name (str): Name of the product.
        * price (float): Price of the product.
        * image (str): Image of the product.
        * description (str): Description of the product.

        """
        product = (
            request.env["product.product"]
            .sudo()
            .search([("id", "=", product_id)], limit=1)
        )
        for rec in product:
            vals = {
                "name": rec.name,
                "price": rec.lst_price,
                "image": rec.image_1920,
                "description": rec.product_tmpl_id.description_sale,
            }
        return vals

    @http.route("/get/panorama/config", type="json", auth="public")
    def get_panorama_config(self):
        """
        This function is used to get the panorama configuration for 360° view of a product.

        Returns:
        A tuple of dictionaries that contains configuration values for the 360°
         panorama view and the hotspot ids for the products.
        """
        record = request.env["panorama.view.config"].sudo().search([], limit=1)
        image_path = modules.get_module_resource('gio_obstgemuese_theme', 'static/src/images/home/', '360_image.jpg')
        panorama_image = base64.b64encode(open(image_path, 'rb').read())
        vals = []
        config = {
            "panorama_image": record.panorama_image if record.panorama_image else panorama_image,
            "auto_rotate": record.auto_rotate,
            "auto_rotate_value": record.auto_rotate_value,
        }
        for rec in record.hotspot_ids:
            hotspot_ids = {
                "pitch": rec.pitch,
                "yaw": rec.yaw,
                "product_id": rec.product_id.id,
            }
            vals.append(hotspot_ids)
        return config, vals


class MassMailController(main.MassMailController):
    @route("/web_mailing/subscribe", type="json", website=True, auth="public")
    def subscribe(self, cargobike, performance, list_id, email, **post):
        """
        Subscribe to a mailing list.

        This function handles the process of subscribing an email to a mailing list.
        If the email already exists, it will update its subscription status. If not, it will
        create a new contact with the given email and add it to the list. The function also
        checks for suspicious activity by validating the reCAPTCHA token.

        :param cargobike: Whether the subscriber is interested in cargo bikes or not.
        :param performance: Whether the subscriber is interested in performance bikes or not.
        :param list_id: ID of the mailing list to subscribe to.
        :param email: Email address of the subscriber.
        :param post: Other parameters sent in the request.
        :return: A dictionary with the result of the operation, including a toast message and its type.
        """
        if not request.env["ir.http"]._verify_request_recaptcha_token(
                "website_mass_mailing_subscribe"
        ):
            return {
                "toast_type": "danger",
                "toast_content": _("Suspicious activity detected"),
            }
        mailing_contact_sub = request.env["mailing.contact.subscription"]
        ContactSubscription = mailing_contact_sub.sudo()
        Contacts = request.env["mailing.contact"].sudo()
        name, email = Contacts.get_name_email(email)
        lst_id = ("list_id", "=", int(list_id))
        email_id = ("contact_id.email", "=", email)
        subscription = ContactSubscription.search([lst_id, email_id], limit=1)
        if not subscription:
            # inline add_to_list as we've already called half of it
            contact_id = Contacts.search([("email", "=", email)], limit=1)
            if not contact_id:
                contact_id = Contacts.create(
                    {
                        "name": name,
                        "email": email,
                        "cargo_bike": cargobike,
                        "performance": performance,
                    }
                )
            ContactSubscription.create(
                {
                    "contact_id": contact_id.id,
                    "list_id": int(list_id),
                }
            )
        elif subscription.opt_out:
            subscription.opt_out = False
        # add email to session
        request.session["mass_mailing_email"] = email
        return {
            "toast_type": "success",
            "toast_content": _("Thanks for subscribing!"),
        }


class WebsiteSaleInherit(WebsiteSale):

    def _get_search_options(
            self, category=None, attrib_values=None, pricelist=None,
            min_price=0.0, max_price=0.0, conversion_rate=1, **post
    ):
        """
        Generate a dictionary of options for search results.

        This function returns a dictionary with the following options for the display of search results:

        displayDescription: (bool) Show/hide product descriptions
        displayDetail: (bool) Show/hide product details
        displayExtraDetail: (bool) Show/hide extra product details
        displayExtraLink: (bool) Show/hide extra links
        displayImage: (bool) Show/hide product images
        allowFuzzy: (bool) Enable/disable fuzzy search based on the "noFuzzy" argument
        category: (str) Category ID to filter the search results. If a category is provided, it will be converted to a string.
        min_price: (float) Minimum price to filter the search results. The value is divided by the conversion rate.
        max_price: (float) Maximum price to filter the search results. The value is divided by the conversion rate.
        attrib_values: (dict) Dictionary of attribute values to filter the search results.
        display_currency: (str) Currency to display the search results.
        Parameters:
        category (odoo.models.Model): The category object to filter the search results by.
        attrib_values (dict): Dictionary of attribute values to filter the search results.
        pricelist (odoo.models.Model): The pricelist object to use to display the search results.
        min_price (float): Minimum price to filter the search results.
        max_price (float): Maximum price to filter the search results.
        conversion_rate (float): The conversion rate to apply to the min_price and max_price values.
        post (dict): Dictionary of other parameters.

        Returns:
        dict: The dictionary of options for the search results.
        """
        return {
            'displayDescription': True,
            'displayDetail': True,
            'displayExtraDetail': True,
            'displayExtraLink': True,
            'displayImage': True,
            'allowFuzzy': not post.get('noFuzzy'),
            'category': str(category.id) if category else None,
            'min_price': min_price / conversion_rate,
            'max_price': max_price / conversion_rate,
            'attrib_values': attrib_values,
            'display_currency': pricelist.currency_id,
        }

    def sitemap_shop_pagination_custom(env, rule, qs):
        """
        Generates a sitemap for shop pagination custom.

        Arguments:
        env: An instance of the odoo environment.
        rule: The URL routing rule.
        qs: The query string of the URL.

        Returns:
        A generator that yields dictionaries containing the 'loc' key and its
        value as the location of the page in the sitemap.
        """
        if not qs or qs.lower() in '/shop':
            yield {'loc': '/shop'}

        Category = env['product.public.category']
        dom = sitemap_qs2dom(qs, '/shop/pagination_category', Category._rec_name)
        dom += env['website'].get_current_website().website_domain()
        for cat in Category.search(dom):
            loc = '/shop/pagination_category/%s' % slug(cat)
            if not qs or qs.lower() in loc:
                yield {'loc': loc}

    @http.route([
        '''/shop/pagination/<int:page>''',
        '''/shop/pagination_category/<model("product.public.category"):category>/page/<int:page>''',
    ], type='json', auth="public", website=True, sitemap=sitemap_shop_pagination_custom)
    def shop_pagination(self, page=0, category=None, search='', min_price=0.0,
                        max_price=0.0, ppg=False, **post):
        """
        This function provides a route for the Odoo e-commerce website to display pagination of shop products.

        The function takes the following parameters:

        page (int): page number of the product listing to display.
        category (model("product.public.category")): category of the products to display.
        search (str): a search string to filter the products by their name or description.
        min_price (float): minimum price of the products to display.
        max_price (float): maximum price of the products to display.
        ppg (bool): number of products per grid.
        post (dict): additional parameters to filter the products by.
        The function also retrieves several values from the Odoo request object:

        ppg: number of products per grid.
        ppr: number of products per row.
        pricelist: pricing list for the products.
        company_currency: currency of the company website.
        conversion_rate: conversion rate of the company currency to the pricing list currency.
        url: URL of the shop page.
        search options: options to filter the products by their price and category.
        product_count: count of products matching the filter criteria.
        details: details of the products matching the filter criteria.
        fuzzy_search_term: fuzzy search term used to search the products.
        search_product: products matching the filter criteria.
        filter_by_price_enabled: flag indicating if filtering by price is enabled on the website.
        available_min_price: minimum available price of the products matching the filter criteria.
        available_max_price: maximum available price of the products matching the filter criteria.
        add_qty: quantity to add to the shopping cart when a product is selected.
        The function returns JSON data to display the pagination of the shop products.
        """
        add_qty = int(post.get('add_qty', 1))
        try:
            min_price = float(min_price)
        except ValueError:
            min_price = 0
        try:
            max_price = float(max_price)
        except ValueError:
            max_price = 0
        Category = request.env['product.public.category']
        if category:
            category = Category.search([('id', '=', int(category))], limit=1)
            if not category or not category.can_access_from_current_website():
                raise NotFound()
        else:
            category = Category

        if ppg:
            try:
                ppg = int(ppg)
                post['ppg'] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            ppg = request.env['website'].get_current_website().shop_ppg or 40

        ppr = request.env['website'].get_current_website().shop_ppr or 4

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if
                         v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}

        keep = QueryURL('/shop', category=category and int(category),
                        search=search, attrib=attrib_list, min_price=min_price,
                        max_price=max_price, order=post.get('order'))

        pricelist_context, pricelist = self._get_pricelist_context()

        request.context = dict(request.context, pricelist=pricelist.id,
                               partner=request.env.user.partner_id)

        filter_by_price_enabled = request.website.is_view_active(
            'website_sale.filter_products_price')
        if filter_by_price_enabled:
            company_currency = request.website.company_id.currency_id
            conversion_rate = request.env['res.currency']._get_conversion_rate(
                company_currency, pricelist.currency_id,
                request.website.company_id, fields.Date.today())
        else:
            conversion_rate = 1

        url = "/shop"
        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list

        options = self._get_search_options(
            category=category,
            attrib_values=attrib_values,
            pricelist=pricelist,
            min_price=min_price,
            max_price=max_price,
            conversion_rate=conversion_rate,
            **post
        )
        product_count, details, fuzzy_search_term = request.website._search_with_fuzzy(
            "products_only", search,
            limit=None, order=self._get_search_order(post), options=options)
        search_product = details[0].get('results', request.env[
            'product.template']).with_context(bin_size=True)

        filter_by_price_enabled = request.website.is_view_active(
            'website_sale.filter_products_price')
        if filter_by_price_enabled:
            Product = request.env['product.template'].with_context(
                bin_size=True)
            domain = self._get_search_domain(search, category, attrib_values)
            from_clause, where_clause, where_params = Product._where_calc(
                domain).get_sql()
            query = f"""
                SELECT COALESCE(MIN(list_price), 0) * {conversion_rate}, COALESCE(MAX(list_price), 0) * {conversion_rate}
                  FROM {from_clause}
                 WHERE {where_clause}
            """
            request.env.cr.execute(query, where_params)
            available_min_price, available_max_price = request.env.cr.fetchone()
            if min_price or max_price:
                if min_price:
                    min_price = min_price if min_price <= available_max_price else available_min_price
                    post['min_price'] = min_price
                if max_price:
                    max_price = max_price if max_price >= available_min_price else available_max_price
                    post['max_price'] = max_price
        website_domain = request.website.website_domain()
        categs_domain = [('parent_id', '=', False)] + website_domain
        if search:
            search_categories = Category.search([('product_tmpl_ids', 'in',
                                                  search_product.ids)] + website_domain).parents_and_self
            categs_domain.append(('id', 'in', search_categories.ids))
        else:
            search_categories = Category
        categs = Category.search(categs_domain)
        if category:
            url = "/shop/category/%s" % slug(category)
        pager = request.website.pager(url=url, total=product_count, page=page,
                                      step=ppg, scope=7, url_args=post)
        offset = pager['offset']
        products = search_product[offset:offset + ppg]
        ProductAttribute = request.env['product.attribute']
        if products:
            attributes = ProductAttribute.search([
                ('product_tmpl_ids', 'in', search_product.ids),
                ('visibility', '=', 'visible'),
            ])
        else:
            attributes = ProductAttribute.browse(attributes_ids)

        layout_mode = request.session.get('website_sale_shop_layout_mode')
        if not layout_mode:
            if request.website.viewref(
                    'website_sale.products_list_view').active:
                layout_mode = 'list'
            else:
                layout_mode = 'grid'
        values = {
            'search': fuzzy_search_term or search,
            'original_search': fuzzy_search_term and search,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'add_qty': add_qty,
            'products': products,
            'search_count': product_count,  # common for all searchbox
            'bins': TableCompute().process(products, ppg, ppr),
            'ppg': ppg,
            'ppr': ppr,
            'categories': categs,
            'attributes': attributes,
            'keep': keep,
            'search_categories_ids': search_categories.ids,
            'layout_mode': layout_mode,
        }
        if filter_by_price_enabled:
            values['min_price'] = min_price or available_min_price
            values['max_price'] = max_price or available_max_price
            values['available_min_price'] = tools.float_round(
                available_min_price, 2)
            values['available_max_price'] = tools.float_round(
                available_max_price, 2)
        if category:
            values['main_object'] = category
        print(values)
        if page > pager.get('page_count'):
            values['template_ok'] = False
            values['pagination_limit'] = True
            return values
        pagination = pager.get('page')['num'] if pager.get('page') else None
        csrf_token = request.csrf_token()
        tr_lis = []
        tr_lis_mobile = []
        for tr_product in values.get('bins'):
            lis = []
            mobile_lis = []
            for td_product in tr_product:
                if td_product:
                    product = td_product.get('product')
                    product_href = str(product.website_url)
                    combination_info = product._get_combination_info(only_template=True, add_qty=add_qty or 1,
                                                                     pricelist=pricelist)
                    combination_info_price = 'block' if combination_info.get('price') else 'none'
                    combination_info_has_discounted_price = '' if combination_info.get(
                        'has_discounted_price') else 'd-none'
                    website_published = 'on' if product.website_published else 'off'
                    product_image_big = 'image_1024' if td_product.get('x') + td_product.get('y') > 2 else 'image_256'
                    product_x_col = 'col-6' if td_product.get('x') == 1 else 'col-12'

                    lis.append(
                        f"""<td colspan='{td_product.get('x')}' rowspan='{td_product.get('y')}' class='oe_product'><div class='o_wsale_product_grid_wrapper o_wsale_product_grid_wrapper_{td_product.get('x')}_{td_product.get('y')}'>

                                <form action='/shop/cart/update' method='post' class='card oe_product_cart' data-publish='{website_published} itemscope='itemscope' itemtype='http://schema.org/Product'>
                                <a class='o_product_link css_editable_mode_hidden' href='{product_href}'/>
                                <div class='card-body p-1 oe_product_image' style='background-color:white !important'>
                                    <input type='hidden' name='csrf_token' value='{csrf_token}' />
                                    <a href='{product_href}' class='d-block h-100' itemprop='url'>
                                        <span class='d-flex h-100 justify-content-center align-items-center'>
                                        <img src='/web/image/product.template/{product.id}/{product_image_big}' itemprop="image" class="img img-fluid" alt="[E-COM08] Storage Box" loading="lazy" style="">
                                        </span></a></div>""" +
                        f""" <div class='card-body p-0 o_wsale_product_information  text-center' style='background-color: white !important; color: black;'>
                                    <div class='p-2 o_wsale_product_information_text'>
                                        <h6 class='o_wsale_products_item_title'>
                                            <a class='text-dark text-decoration-none GT_Pressura_Regular' itemprop='name' href='{product_href}' content='{product.name}'>{product.name}</a>
                                        </h6>
                                        <div class='product_price mb-1' itemprop='offers' itemscope='itemscope' itemtype='http://schema.org/Offer'>
                                        
                                          <span data-oe-type="monetary" style='display: {combination_info_price} !important; ' data-oe-expression="combination_info['price']" class="GT_Pressura_Regular">$&nbsp;<span class="oe_currency_value">{combination_info.get('price')}</span></span>
                                            <del data-oe-type="monetary" data-oe-expression="combination_info['list_price']" style="white-space: nowrap;" class="text-danger GT_Pressura_Regular ml-1 h6 {combination_info_has_discounted_price}">$&nbsp;<span class="oe_currency_value">{combination_info.get('combination_info_has_discounted_price')}</span></del>
                                            <span itemprop="price" style="display:none;">{combination_info.get('price')}</span>
                                            <span itemprop="priceCurrency" style="display:none;">{request.website.currency_id.name}</span>
                                        
                                        </div>
                                    </div>
                                    <div class='o_wsale_product_btn pl-2 d-none'/>
                                </div>
                            </form> </div></td>""")
                    mobile_lis.append(
                        f"""<div colspan='{td_product.get('x')}' rowspan='{td_product.get('y')}' class='oe_product {product_x_col}'>
                                            <div class='o_wsale_product_grid_wrapper o_wsale_product_grid_wrapper_{td_product.get('x')}_{td_product.get('y')}'>
                                                
                                                <form action='/shop/cart/update' method='post' class='card oe_product_cart' data-publish='{website_published} itemscope='itemscope' itemtype='http://schema.org/Product'>
                                                    <a class='o_product_link css_editable_mode_hidden' href='{product_href}'/>
                                                        <div class='card-body p-1 oe_product_image' style='background-color:white !important'>
                                                        <input type='hidden' name='csrf_token' value='{csrf_token}' />
                                                        <a href='{product_href}' class='d-block h-100' itemprop='url'>
                                                            <span class='d-flex h-100 justify-content-center align-items-center'>
                                                            <img src='/web/image/product.template/{product.id}/{product_image_big}' itemprop="image" class="img img-fluid" alt="[E-COM08] Storage Box" loading="lazy" style="">
                                                            </span></a></div>""" +
                        f""" <div class='card-body p-0 o_wsale_product_information  text-center' style='background-color: white !important; color: black;'>
                                                        <div class='p-2 o_wsale_product_information_text'>
                                                            <h6 class='o_wsale_products_item_title'>
                                                                <a class='text-dark text-decoration-none GT_Pressura_Regular' itemprop='name' href='{product_href}' content='{product.name}'>{product.name}</a>
                                                            </h6>
                                                            <div class='product_price mb-1' itemprop='offers' itemscope='itemscope' itemtype='http://schema.org/Offer'>
                                                            
                                                              <span data-oe-type="monetary" style='display: {combination_info_price} !important; ' data-oe-expression="combination_info['price']" class="GT_Pressura_Regular">$&nbsp;<span class="oe_currency_value">{combination_info.get('price')}</span></span>
                                                                <del data-oe-type="monetary" data-oe-expression="combination_info['list_price']" style="white-space: nowrap;" class="text-danger GT_Pressura_Regular ml-1 h6 {combination_info_has_discounted_price}">$&nbsp;<span class="oe_currency_value">{combination_info.get('combination_info_has_discounted_price')}</span></del>
                                                                <span itemprop="price" style="display:none;">{combination_info.get('price')}</span>
                                                                <span itemprop="priceCurrency" style="display:none;">{request.website.currency_id.name}</span>
                                                            
                                                            </div>
                                                        </div>
                                                        <div class='o_wsale_product_btn pl-2 d-none'/>
                                                    </div>
                                                </form> 
                                                
                                                </div>
                                            </div>""")
            tr_lis.append("<tr>" + ','.join(lis) + "</tr>")
            tr_lis_mobile.append("<div class='row'>" + ','.join(mobile_lis) + "</div>")
        values['tr_lis'] = ','.join(tr_lis).replace('\n', ' ')
        values['tr_lis_mobile'] = ','.join(tr_lis_mobile).replace('\n', ' ').replace(",", "")
        values['template_ok'] = True
        return values

    def _prepare_product_values(self, product, category, search, **kwargs):
        res = super(WebsiteSaleInherit, self)._prepare_product_values(product=product, category=category, search=search,
                                                                      **kwargs)
        stories_obj = request.env['blog.post']
        related_stories = stories_obj.sudo().search(
            [('product_template_ids', 'in', product.id), ('public_categ_ids', 'in', product.public_categ_ids.ids)])
        if not related_stories:
            res['has_related_stories'] = False
            return res
        related_stories = list(related_stories)
        random.shuffle(related_stories)
        res['related_story'] = related_stories[0]
        res['related_stories'] = related_stories
        res['has_related_stories'] = True
        return res

    @http.route('/performance', type="http", auth="public", website=True)
    def _get_performance_page(self):
        return request.render("gio_obstgemuese_theme.performance")
