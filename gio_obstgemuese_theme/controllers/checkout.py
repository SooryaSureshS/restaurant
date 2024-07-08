# Company: giordano.ch AG
# Copyright by: giordano.ch AG
# https://giordano.ch/

import logging
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request
from odoo import http, tools, _
from werkzeug.exceptions import Forbidden
_logger = logging.getLogger(__name__)


class WebsiteSaleInherit(WebsiteSale):
    @http.route("/process/checkout/page", type="http", auth="public", website=True)
    def process_checkout_custom(self, **post):
        """
        This function processes the checkout page, replacing the shop/checkout,
         address, and payment pages.
        It returns the sale order partner object, along with several values
        related to the order, partner, and payment information.
        """
        order = request.website.sale_get_order()
        values = self.checkout_values(**post)
        values.update({"website_sale_order": order})
        template = "gio_obstgemuese_theme.custom_checkout_obst"
        redirection = self.checkout_redirection(order)
        if redirection:
            return request.redirect("/shop")
        order_partner_id = order.partner_id.id
        user_partner_id = request.website.user_id.sudo().partner_id.id
        values.update({
            "order_partner_id": order_partner_id,
            "user_partner_id": user_partner_id,
        })
        render_values = self._get_shop_payment_values(order, **post)
        render_values["only_services"] = order and order.only_services or False
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            values.update(
                self._get_country_related_render_valuesa(render_values))
            return request.render(template, values)
        if render_values["errors"]:
            render_values.pop("acquirers", "")
            render_values.pop("tokens", "")
        values.update(render_values)
        redirection = self.checkout_check_address(order)
        if redirection:
            values['address_redirection'] = True
        if post.get("express"):
            return request.redirect("/shop/confirm_order")
        if post.get("xhr"):
            return "ok"
        values.update(
            self._get_country_related_render_valuesa(render_values))
        self.confirm_order(**post)
        return request.render(template, values)

    def confirm_order(self, **post):
        """
        Confirms the order by getting the current website order, checking the
        redirection and address, updating the tax, saving the last order ID to
        the session, updating the pricelist and returning True.

        Returns:
        bool: True
        """
        order = request.website.sale_get_order()

        redirection = self.checkout_redirection(
            order) or self.checkout_check_address(order)
        order.onchange_partner_shipping_id()
        order.order_line._compute_tax_id()
        request.session['sale_last_order_id'] = order.id
        request.website.sale_get_order(update_pricelist=True)
        extra_step = request.website.viewref('website_sale.extra_info_option')
        return True

    @staticmethod
    def _get_country_related_render_valuesa(render_values):
        """
        Returns the related countries and partner states for the checkout process.

        Args:
            render_values: A dictionary containing values related to the checkout process.

        Returns:
            A dictionary containing the following keys:
            - country: The default country for the order's partner.
            - country_states: The states for the default country.
            - countries: The list of countries available for the checkout process.
        """
        order = render_values.get('website_sale_order')

        def_country_id = order.partner_id.country_id
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            country_code = request.session['geoip'].get('country_code')
            if country_code:
                def_country_id = request.env['res.country'].search(
                    [('code', '=', country_code)], limit=1)
            else:
                def_country_id = request.website.user_id.sudo().country_id
        res = {
            'country': def_country_id,
            'country_states': def_country_id.get_website_sale_states(),
            'countries': def_country_id.get_website_sale_countries(),
        }
        return res


class CheckOut(http.Controller):

    @http.route('/process/checkout/address', type="json", auth="public", methods=['GET', 'POST'], csrf=False)
    def process_checkout_address(self, **kwargs):
        """
        process_checkout_address(self, **kwargs)

        Edit or add shipping and billing address information during checkout process.

        Route: "/process/checkout/address"
        Methods: GET, POST
        Access: Public
        CSRF Protection: Disabled

        This function takes in kwargs as arguments and retrieves data from the
        website environment. The retrieved data is then preprocessed and
        validated for errors. If the data is valid, it is then processed and
        saved to the sale order, updating the billing or shipping address
        information. If there are errors, the function returns a dictionary
        with the 'status' key set to False and the error message. If the
        address information is updated successfully, the function returns a
        dictionary with the 'status' key set to True and a success message.
        In case of any exceptions, the function returns a dictionary with the
        'status' key set to 0 and the error message.
        """
        try:
            data = kwargs
            website = request.env['website'].browse(request.website_routing)
            order_id = data.get('sale_order_id')
            order = request.env['sale.order'].sudo().search([('id', '=', int(order_id))])
            mode = data.get('mode')
            pre_values = self.values_preprocess(data)
            errors, error_msg = self.checkout_form_validate(pre_values)
            if errors:
                return {
                    'status': False,
                    'message': error_msg
                }
            post = self.values_postprocess(order, mode, pre_values, website)
            partner_id = self._checkout_form_save(mode, post, data, order)
            if mode[1] == 'billing':
                order.partner_id = partner_id
                order.with_context(
                    not_self_saleperson=True).onchange_partner_id()
                order.partner_invoice_id = partner_id
            elif mode[1] == 'shipping':
                order.partner_shipping_id = partner_id
            order.message_partner_ids = [(4, partner_id), (3, website.partner_id.id)]
            return {
                'status': True,
                'message': 'Billing Address Updated Successfully'
            }
        except Exception as e:
            return {
                'status': 0,
                'message': e
            }

    @staticmethod
    def checkout_values(order, **kw):
        """
        Generates a dictionary of checkout values with the delivery address information

        Args:
        order (object): Object of order class
        **kw: Additional arguments

        Returns:
        dict: Dictionary containing the delivery address information
        {
        'delivery_address': Delivery address information in dictionary format,
        'mode': Mode of operation ('edit' if delivery address exists, 'new' otherwise)
        }
        """
        delivery_address = []
        website = request.env['website'].browse(request.website_routing)
        if order.partner_id != website.user_id.sudo().partner_id:
            Partner = order.partner_id.with_context(show_address=1).sudo()
            shipping = Partner.search([
                ("id", "child_of", order.partner_id.commercial_partner_id.ids),
                '|', ("type", "in", ["delivery", "other"]), ("id", "=", order.partner_id.commercial_partner_id.id)
            ], order='id desc')
            if shipping:
                if kw.get('partner_id') or 'use_billing' in kw:
                    if 'use_billing' in kw:
                        partner_id = order.partner_id.id
                    else:
                        partner_id = int(kw.get('partner_id'))
                    if partner_id in shipping.mapped('id'):
                        order.partner_shipping_id = partner_id
            delivery_address = [{'name': address.name,
                                 'id': address.id,
                                 'company_name': address.parent_id.name,
                                 'phone': address.phone,
                                 'street': address.street,
                                 'street2': address.street2,
                                 'city': address.city,
                                 'state_id': {'id': address.state_id.id,
                                              'name': address.state_id.name} if address.state_id else {},
                                 'zip': address.zip,
                                 'country_id': {'id': address.country_id.id, 'name': address.country_id.name}} for
                                address in list(filter(lambda ship: ship == order.partner_shipping_id, shipping))]
        return {
            'delivery_address': delivery_address[0] if delivery_address else None,
            'mode': 'edit' if delivery_address else 'new'
        }

    @staticmethod
    def values_preprocess(values):
        """
        Convert the values for many2one fields to integers since they are used as IDs in res.partner model

        Parameters:
        values (dict): Dictionary of values to be processed

        Returns:
        dict: Dictionary of processed values with many2one fields converted to integers

        """
        partner_fields = request.env['res.partner']._fields
        return {
            k: (bool(v) and int(v)) if k in partner_fields and partner_fields[k].type == 'many2one' else v
            for k, v in values.items()
        }

    @staticmethod
    def values_postprocess(order, mode, values, website):
        """
         Process customer order values to update new_values dictionary.

         Args:
         - order (object): The customer order object.
         - mode (tuple): Mode of the customer order, consisting of two values
            (edit/new, billing/shipping).
         - values (dict): The original customer order values.
         - website (object): The website object associated with the customer
            order.

         Returns:
         - dict: The updated new_values dictionary, containing only authorized
            fields with non-null values.
         Additional values, such as website ID, company ID, sales team ID,
            salesperson ID, and customer type, may be added based on the
            specified mode.

         """
        new_values = {}
        authorized_fields = request.env['ir.model']._get('res.partner')._get_form_writable_fields()
        for k, v in values.items():
            if k in authorized_fields and v is not None:
                new_values[k] = v
            else:
                if k not in ('field_required', 'partner_id', 'callback',
                             'submitted'):
                    _logger.debug(
                        "website_sale postprocess: %s value has been dropped (empty or not writable)" % k)

        if website.specific_user_account:
            new_values['website_id'] = website.id

        if mode[0] == 'new':
            new_values['company_id'] = website.company_id.id
            new_values[
                'team_id'] = website.salesteam_id and website.salesteam_id.id
            new_values['user_id'] = website.salesperson_id.id
        if mode == ('edit', 'billing') and order.partner_id.type == 'contact':
            new_values['type'] = 'other'
        if mode[1] == 'shipping':
            new_values['parent_id'] = order.partner_id.commercial_partner_id.id
            new_values['type'] = 'delivery'

        return new_values

    @staticmethod
    def checkout_form_validate(data):
        """
        Validate the customer checkout form data.

        Args:
        - data (dict): The customer checkout form data.

        Returns:
        - tuple: A two-element tuple containing the validation error dictionary
         and a list of error messages.
        The error dictionary maps field names to error codes, where 'missing'
        indicates a missing required field and 'error' indicates an invalid
        field value.
        The error message list contains human-readable error descriptions.

        """
        error = dict()
        error_message = []
        required_fields = ['name', 'phone', 'street', 'city', 'zip', 'country_id']
        for field_name in required_fields:
            if not data.get(field_name):
                error[field_name] = 'missing'
        if data.get('email') and not tools.single_email_re.match(data.get('email')):
            error["email"] = 'error'
            error_message.append(_('Invalid Email! Please enter a valid email address.'))
        if [err for err in error.values() if err == 'missing']:
            error_message.append(_('Some required fields are empty.'))

        return error, error_message

    @staticmethod
    def _checkout_form_save(mode, checkout, all_values, order):
        """
        This function is used to save data from a checkout form to the database.

        Args:
        mode (Tuple[str, str]): Mode of operation, either "new" to create a new
            partner or "edit" to modify an existing one.
        checkout (Dict): Data to be saved.
        all_values (Dict): All values submitted in the checkout form.
        order (Object): The current order.

        Returns:
        int: The ID of the saved or modified partner.

        Raises:
        Forbidden: If the provided partner ID is not a child of the commercial
            partner ID or if it doesn't match the order's partner ID.
        """
        Partner = request.env['res.partner']
        if mode[0] == 'new':
            partner_id = Partner.sudo().with_context(tracking_disable=True).create(checkout).id
        elif mode[0] == 'edit':
            partner_id = int(all_values.get('partner_id', 0))
            if partner_id:
                shippings = Partner.sudo().search([("id", "child_of", order.partner_id.commercial_partner_id.ids)])
                if partner_id not in shippings.mapped('id') and partner_id != order.partner_id.id:
                    return Forbidden()
                Partner.browse(partner_id).sudo().write(checkout)
        return partner_id

    @http.route(['/shop/country_info/<model("res.country"):country>'],
                type='json', auth="public", methods=['POST'], website=True)
    def country_info(self, country, **kw):
        """
           Return country information including its address fields, states,
            phone code, zip requirement, and state requirement.

           :param country: The country to retrieve information for.
           :type country: model('res.country')
           :return: A dictionary containing information about the country.
           :rtype: dict
        """

        return dict(
            fields=country.get_address_fields(),
            states=[(st.id, st.name, st.code) for st in
                    country.get_website_sale_states()],
            phone_code=country.phone_code,
            zip_required=country.zip_required,
            state_required=country.state_required,
        )

    @http.route('/website_mass_mailing/subscribe', type='json', website=True, auth="public")
    def website_mass_mailing_subscribe(self, list_id, email, **post):
        """
        Subscribe a user to a mailing list

        Args:
            list_id (int): The ID of the mailing list to subscribe to.
            email (str): The email address of the user to subscribe.

        Returns:
            dict: A JSON-serializable dictionary with a toast message to display
             on the frontend. The keys are:
                - toast_type (str): The type of toast to display, either
                'success' or 'danger'.
                - toast_content (str): The content of the toast message.

        Raises:
            Forbidden: If the user's request is detected as suspicious by
            Google reCaptcha.
        """
        if not request.env['ir.http']._verify_request_recaptcha_token('website_mass_mailing_subscribe'):
            return {
                'toast_type': 'danger',
                'toast_content': _("Suspicious activity detected by Google reCaptcha."),
            }
        ContactSubscription = request.env['mailing.contact.subscription'].sudo()
        Contacts = request.env['mailing.contact'].sudo()
        name, email = Contacts.get_name_email(email)

        subscription = ContactSubscription.search([('list_id', '=', int(list_id)), ('contact_id.email', '=', email)],
                                                  limit=1)
        if not subscription:
            contact_id = Contacts.search([('email', '=', email)], limit=1)
            if not contact_id:
                contact_id = Contacts.create({'name': name, 'email': email})
            ContactSubscription.create({'contact_id': contact_id.id, 'list_id': int(list_id)})
        elif subscription.opt_out:
            subscription.opt_out = False
        request.session['mass_mailing_email'] = email
        return {
            'toast_type': 'success',
            'toast_content': _("Thanks for subscribing!"),
        }
