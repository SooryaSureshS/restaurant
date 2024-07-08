import werkzeug
import logging

from odoo.http import request
from odoo import http, _
from odoo.exceptions import UserError

from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.auth_signup.controllers.main import ensure_db, AuthSignupHome as Home
from odoo.addons.web.controllers.main import SIGN_UP_REQUEST_PARAMS

_logger = logging.getLogger(__name__)

SIGN_UP_REQUEST_PARAMS.add('mobile_login')


class AuthSignupHome(Home):

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        """
        Override the authentication sign-up route to validate email/mobile and add user information.

        This function adds validation for email/mobile input and also updates user's partner address information.
        If the sign-up is successful, it sends a confirmation email, authenticates the user and redirects to the
        homepage. If there is an error during the sign-up process, an error message will be displayed on the page.

        Returns:
            A HTTP response that renders the sign-up page with a success or error message.

        Raises:
            UserError: If there is an error during user input validation.
            SignupError: If there is an error during user creation.
            AssertionError: If there is an error with the email/mobile validation.
        """
        qcontext = self.get_auth_signup_qcontext()
        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                self.do_signup(qcontext)
                # Send an account creation confirmation email
                User = request.env['res.users']
                user_sudo = User.sudo().search(
                    User._get_login_domain(qcontext.get('login')), order=User._get_login_order(), limit=1
                )
                template = request.env.ref('auth_signup.mail_template_user_signup_account_created', raise_if_not_found=False)
                if user_sudo and template:
                    template.sudo().send_mail(user_sudo.id, force_send=True)
                uid = request.session.authenticate(request.session.db, request.params['login'],
                                                   request.params['password'])
                request.params['login_success'] = True
                if user_sudo:
                    user_sudo.partner_id.sudo().write({'street': kw.get('street'),
                                                       'street2': kw.get('location'),
                                                       'city': kw.get('location'),
                                                       'state_id': int(kw.get('state_id')),
                                                       'zip': kw.get('zip'),
                                                       'country_id': int(kw.get('country_id'))
                                                       })
                if kw.get('delivery_address') == 'on':
                    child_id = self.add_shipping_address(**kw)
                    user_sudo.partner_id.child_ids = [(4, child_id.id)]
                return request.redirect(self._login_redirect(uid, redirect='/'))
                # return self.web_login(*args, **kw)
            except UserError as e:
                qcontext['error'] = e.name or e.value
            except (SignupError, AssertionError) as e:
                if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                    qcontext["error"] = _("Another user is already registered using this email address/Mobile Number.")
                else:
                    if not qcontext['login'] and not qcontext['mobile']:
                        _logger.error(e.message)
                        qcontext['error'] = _("Please Enter Email or Mobile.")
                    else:
                        _logger.error("%s", e)
                        qcontext['error'] = _("Could not create a new account.")

        response = request.render('auth_signup.signup', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @staticmethod
    def add_shipping_address(**kw):
        """
        Create a new shipping address for a customer.

        Args:
        kw (dict): Keyword arguments, where each key represents a field name and its value is the field value.
        The keys that start with "delivery_" will be used to create the new address.

        Returns:
        res.partner: The created partner (shipping address).
        """
        vals = {n.replace('delivery_', ''): kw.get(n) for n in kw.keys() if n.startswith("delivery_")}
        vals['email'] = kw.get('login')
        if vals.get('country_id'):
            vals['country_id'] = int(vals.get('country_id'))
        if vals.get('state_id'):
            vals['state_id'] = int(vals.get('state_id'))
        list(map(lambda x: vals.pop(x), ['address', 'last_name']))
        Partner = request.env['res.partner']
        partner = Partner.sudo().with_context(tracking_disable=True).create(vals)
        request.env.cr.commit()
        return partner

    @staticmethod
    def update_partner(partner_obj, **kw):
        """
        Update the address details of a partner in Odoo.

        Args:
        partner_obj (res.partner): Object of the partner to be updated.
        kw (dict): Dictionary containing the new address details.

        Returns:
        None
        """
        partner_obj.sudo().write({'street': kw.get('street'),
                                  'street2': kw.get('location'),
                                  'city': '',
                                  'state_id': kw.get('state_id'),
                                  'zip': kw.get('zip'),
                                  'country_id': kw.get('country_id')})

    def _prepare_signup_values(self, qcontext):
        """Prepare the values used to create a new user during signup.

        This function extends the base implementation by adding the mobile field to the
        created res.partner object.

        Args:
        qcontext (dict): The context passed to the signup view.

        Returns:
        dict: The values to use when creating the new user and partner.

        Raises:
        UserError: If a user is already registered with the provided email or login.
        """
        values = super(AuthSignupHome, self)._prepare_signup_values(qcontext)
        _find_partner = lambda login: request.env["res.partner"].sudo().search([("email", "=", login)])
        if _find_partner(qcontext.get("login")) or _find_partner(qcontext.get("email")):
            raise UserError(_("A user is already registered using this email address."))
        values.update(dict(
            email=qcontext.get('email'),
            mobile=qcontext.get('mobile')
        ))
        return values

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        """Routes the user to the web login page.

        This method is responsible for routing the user to the web login page. Before routing, it checks the database and updates the context with the country related render values.

        Arguments:
        redirect (str, optional): The URL to redirect the user after a successful login. Defaults to None.
        **kw: Additional keyword arguments to pass to the parent class' web_login method.

        Returns:
        A response object containing the rendered web login page.
        """
        ensure_db()
        res = super(AuthSignupHome, self).web_login(redirect, **kw)
        res.qcontext.update(
            self._get_country_related_render_value())
        return res

    @staticmethod
    def _get_country_related_render_value():
        """
        Return the country-related values for rendering on the website.

        Returns:
        dict: A dictionary containing the following keys:
        - country: The default country.
        - country_states: The partner states associated with the default country.
        - countries: The available countries for website sales.
        """
        def_country_id = request.env['res.country'].search([])
        res = {
            'country': "",
            'country_states': "",
            'countries': def_country_id.get_website_sale_countries(),
        }
        return res
