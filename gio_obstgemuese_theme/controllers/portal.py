# Company: giordano.ch AG
# Copyright by: giordano.ch AG
# https://giordano.ch/

import logging
from werkzeug.exceptions import Forbidden
from odoo.http import request, route
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo import http, tools, _

_logger = logging.getLogger(__name__)


class PortalAccount(http.Controller):
    @http.route("/account/save/Fl_name_picture", type="json", auth="user")
    def save_first_last_name_picture(self, **kw):
        """
        Save first and last name along with profile picture for a user.

        This function updates the first name, last name, and profile picture of
        the user in the database.
        The name is constructed by concatenating the first name and last name
        provided as parameters.

        :param first_name: First name of the user.
        :param last_name: Last name of the user.
        :param image: Profile picture of the user in base64 encoded format.
        :return: Returns True if the operation was successful, otherwise raises
        an exception.
        :rtype: bool
        """
        partner = request.env.user.partner_id
        name = self.concat_name(kw.get("first_name"), kw.get("last_name"))
        if kw.get("image"):
            img = kw.get("image").split(",")[1]
            values = {"name": name, "image_1920": img}
        else:
            values = {
                "name": name,
            }
        if partner.sudo().write(values):
            return True

    def concat_name(self, first, last):
        """
        Concatenate first name and last name

        This function takes two arguments: first and last, and concatenates
        them with a space in between.

        Args:
        first (str): The first name.
        last (str): The last name.

        Returns:
        str: The concatenated first and last name.
        """
        return first + " " + last

    @http.route("/change/password", type="json", auth="user")
    def portal_change_password(self, **kw):
        """
        This function is a route to change the password for a portal user.

        @param kw: Keyword arguments passed to the function
        @return: Returns "change" if the password is successfully updated,
        "nochange" if the password is not changed and "error" if the
        authentication fails
        """
        res_users = request.env["res.users"].sudo()
        password = kw.get("password")
        new_pw = kw.get("conf_password")
        access = self.portal_authenticate(password, res_users)
        uid = request.uid
        if access:
            change_pw = self.update_password(res_users, uid, new_pw)
            return "change" if change_pw else "nochange"
        else:
            return "error"

    def update_password(self, res_users, uid, new_pw):
        """
        Update password for the user

        Arguments:
        res_users (res.users) : res.users object
        uid (int) : ID of the user who wants to change their password
        new_pw (str) : New password entered by the user

        Returns:
        bool : True if password is successfully updated else False
        """
        ctx = res_users._crypt_context()
        hash_password = ctx.hash if hasattr(ctx, "hash") else ctx.encrypt
        query = "UPDATE res_users SET password=%s WHERE id=%s"
        request.cr.execute(query, (hash_password(new_pw), uid))
        return True

    @http.route("/change/email", type="json", auth="user")
    def portal_change_email(self, **kw):
        """
        This function handles the route "/change/email" with type "json" and
        requires user authentication.
        It changes the email address of the current logged-in user if the
        authentication process is successful.
        The authentication process requires the current password to be provided
         along with the new email address.

        Input:
        kw (dictionary): A dictionary with the following keys:
        * password (str): The current password of the user.
        * conf_new_email (str): The new email address to be set for the user.

        Output:
        str: A string indicating the result of the email change operation:
        * "change": The email address was changed successfully.
        * "nochange": The email address was not changed.
        * "error": The provided current password was incorrect.
        * "exist": The provided new email address already exists.
        """
        res_users = request.env["res.users"].sudo()
        email = kw.get("conf_new_email")
        check_login = self.check_exist_login(email, res_users)
        if not check_login:
            res_partner = request.env["res.partner"].sudo()
            password = kw.get("password")
            access = self.portal_authenticate(password, res_users)
            if access:
                vals = {
                    "res_users": res_users,
                    "res_partner": res_partner,
                    "email": email,
                }
                email_change = self.change_email(vals)
                return "change" if email_change else "nochange"
            else:
                return "error"
        else:
            return "exist"

    def change_email(self, vals):
        """
        Changes the email address of the user and his corresponding partner

        Args:
            vals (dict): A dictionary that contains the information of the user
             and partner

        Returns:
            bool: True if email address of the user and his corresponding
            partner is changed, False otherwise

        """
        uid = request.uid
        partner_id = request.env.user.partner_id.id
        user = vals.get("res_users").search([("id", "=", uid)])
        partner = vals.get("res_partner").search([("id", "=", partner_id)])
        user_val = user.write({"login": vals.get("email")})
        partner_val = partner.write({"email": vals.get("email")})
        return user_val and partner_val if user_val and partner_val else False

    def check_exist_login(self, email, res_users):
        """
        Check if the given email already exists in the system as a login.

        Arguments:
        email (str): The email to check if already exists in the system.
        res_users (odoo.models.Model): The res.users model to perform the
        search on.

        Returns:
        odoo.models.Model: If a match is found, returns the matching record.
        bool: If no match is found, returns False.
        """
        return (
            res_users.search([("login", "=", email)])
            if res_users.search([("login", "=", email)])
            else False
        )

    def portal_authenticate(self, password, res_users):
        """
        This function portal_authenticate verifies the provided password
        against the password stored in the database for a user.

        Inputs:
        password (str): The password entered by the user.
        res_users (odoo.models.Model): Odoo model for the user database.

        Returns:
        bool: True if the password matches the stored password for the user,
        False otherwise.
        """
        uid = request.uid
        assert password
        request.cr.execute(
            "SELECT COALESCE(password, '') FROM res_users WHERE id=%s", [uid]
        )
        [hashed] = request.cr.fetchone()
        crypt = res_users._crypt_context()
        valid, replacement = crypt.verify_and_update(password, hashed)
        if replacement is not None:
            res_users._set_encrypted_password(request.uid, replacement)
        if not valid:
            return False
        else:
            return True

    @http.route('/my/account/address', type="json", auth="public", methods=['GET', 'POST'], csrf=False)
    def portal_address(self, **kwargs):
        """
        Handles the editing or adding of shipping and billing address from the
        process checkout page.

        Args:
            kwargs (dict): The data passed in the request.

        Returns:
            dict: A dictionary with the keys `status` and `message`. `status`
            is a boolean indicating whether the operation was successful, and
            `message` is a string with a success or error message.

        Raises:
            Exception: If any error occurs during the execution of the function.
        """
        try:
            data = kwargs
            website = request.env['website'].browse(request.website_routing)
            mode = data.get('mode')
            pre_values = self.portal_values_preprocess(data)
            errors, error_msg = self.portal_checkout_form_validate(pre_values)
            if errors:
                return {
                    'status': False,
                    'message': error_msg
                }
            post = self.portal_values_postprocess(mode, pre_values, website)
            partner_id = self._portal_checkout_form_save(mode, post, data)
            # if mode[1] == 'billing':
            #     order.partner_id = partner_id
            #     order.with_context(
            #         not_self_saleperson=True).onchange_partner_id()
            #     order.partner_invoice_id = partner_id
            # elif mode[1] == 'shipping':
            #     order.partner_shipping_id = partner_id
            # order.message_partner_ids = [(4, partner_id), (3, website.partner_id.id)]
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
    def portal_checkout_form_validate(data):
        """
        This function validates the input data from checkout form.

        Args:
        data (dict): The input data from checkout form.

        Returns:
        tuple: A tuple containing two elements:
        error (dict): A dictionary indicating which field(s) is/are invalid.
        error_message (list): A list of error messages indicating what is wrong with the input data.

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
    def portal_values_preprocess(values):
        """
        Preprocess the values provided by the user to be able to use them in
        creating/updating a partner record.

        This function takes in a dictionary of values, values, and returns a
        modified version of this dictionary where any value corresponding to
        a many2one field in the res.partner model has been converted to an
        'integer.

        Args:
        values (dict): A dictionary of values provided by the user to be used
        for creating/updating a partner record.

        Returns:
        dict: A modified version of the input values dictionary, with any value
        corresponding to a many2one field in the res.partner model converted to
         an integer.
        """
        partner_fields = request.env['res.partner']._fields
        return {
            k: (bool(v) and int(v)) if k in partner_fields and partner_fields[k].type == 'many2one' else v
            for k, v in values.items()
        }

    @staticmethod
    def portal_values_postprocess(mode, values, website):
        """
        This function postprocesses the values of the form fields submitted on the checkout page for shipping or billing address.
        It filters out the authorized fields for writing in the 'res.partner' model and returns the processed values.

        Arguments:
        mode (str): the mode of the form submission, either 'shipping' or 'billing'
        values (dict): the raw form field values submitted
        website (res.website object): the website instance to which the checkout belongs

        Returns:
        new_values (dict): the filtered form field values that are authorized for writing in the 'res.partner' model
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
        return new_values

    @staticmethod
    def _portal_checkout_form_save(mode, checkout, all_values):
        """
        Save the shipping or billing address of the customer to the database.

        This function can either create a new address or edit an existing one,
        depending on the mode argument.

        Arguments:
        mode (list): a list containing the mode of operation ('new' or 'edit')
        and the type of address ('shipping' or 'billing')
        checkout (dict): a dictionary of values to be saved
        all_values (dict): a dictionary containing all the values passed to the
         form, including the partner_id of the address being edited
         (if in 'edit' mode)

        Returns:
        int: the ID of the address (partner) that was saved
        """
        Partner = request.env['res.partner']
        if mode[0] == 'new':
            partner_id = Partner.sudo().with_context(tracking_disable=True).create(checkout).id
        elif mode[0] == 'edit':
            partner_id = int(all_values.get('partner_id', 0))
            if partner_id:
                shippings = Partner.sudo().search([("id", "child_of", request.env.user.partner_id.commercial_partner_id.ids)])
                if partner_id not in shippings.mapped('id') and partner_id != request.env.user.partner_id.id:
                    return Forbidden()
                Partner.browse(partner_id).sudo().write(checkout)
        return partner_id


class CustomerPortalInherit(CustomerPortal):

    @route(['/my', '/my/home'], type='http', auth="user", website=True)
    def home(self, **kw):
        """
        Route and render the My/Home page for a user with authentication.

        This function returns the My/Home page for a user who is logged in.
        It provides an updated view of the user's address information and
        displays the countries and states related to the user's country.
        It also lists the shipping addresses associated with the user's partner

        :return: rendered HTML template of the My/Home page
        :rtype: str
        """
        def _get_country_related_render_vals():
            """
            return countries and partner states
            """
            def_country_id = request.env.user.partner_id.country_id
            res = {
                'country': def_country_id,
                'country_states': def_country_id.get_website_sale_states(),
                'countries': def_country_id.get_website_sale_countries(),
            }
            return res
        values = self._prepare_portal_layout_values()
        values.update(_get_country_related_render_vals())
        Partner = request.env.user.partner_id
        shippings = Partner.search([
            ("id", "child_of", Partner.commercial_partner_id.ids),
            '|', ("type", "in", ["delivery", "other"]),
            ("id", "=", Partner.commercial_partner_id.id)
        ], order='id desc')
        values['shipping'] = shippings
        return request.render("portal.portal_my_home", values)
