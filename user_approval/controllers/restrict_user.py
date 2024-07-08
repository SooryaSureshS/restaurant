import base64

from odoo import http
from odoo.http import request
from odoo.tools.translate import _
from odoo.addons.web.controllers.home import Home
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.user_approval.models.res_users import ApprovalException

SIGN_UP_REQUEST_PARAMS = {'db', 'login', 'debug', 'token', 'message', 'error', 'scope', 'mode',
                          'redirect', 'redirect_hostname', 'email', 'name', 'partner_id',
                          'password', 'confirm_password', 'country_id', 'state_id', 'lang', 'signup_email',
                          'shop', 'phone', 'mobile', 'street', 'city'}


class HomeController(Home):

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        try:
            res = super(HomeController, self).web_login(redirect, **kw)
            return res
        except ApprovalException as e:
            values = {k: v for k, v in request.params.items() if k in SIGN_UP_REQUEST_PARAMS}
            values['error'] = e.args[0]
            response = request.render('web.login', values)
            response.headers['X-Frame-Options'] = 'SAMEORIGIN'
            response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
            return response


class RestrictUser(http.Controller):

    @http.route('/restrict-user', type='json', auth="public", methods=['POST'],
                website=True, csrf=False)
    def restrict_user(self, **kwargs):
        """Checks whether a public user, then redirects to login page if public user"""
        if request.env.user.id == 4 and kwargs.get('loc').split('?')[0] in [item.url for item in
                                                                            request.website.private_urls]:
            return True
        return False


class AuthSignupHomeInh(AuthSignupHome):

    def get_auth_signup_qcontext(self):
        """ Shared helper returning the rendering context for signup and reset password """
        qcontext = {k: v for (k, v) in request.params.items() if k in SIGN_UP_REQUEST_PARAMS}
        qcontext.update(self.get_auth_signup_config())
        if not qcontext.get('token') and request.session.get('auth_signup_token'):
            qcontext['token'] = request.session.get('auth_signup_token')
        if qcontext.get('token'):
            try:
                # retrieve the user info (name, login or email) corresponding to a signup token
                token_infos = request.env['res.partner'].sudo().signup_retrieve_info(qcontext.get('token'))
                for k, v in token_infos.items():
                    qcontext.setdefault(k, v)
            except:
                qcontext['error'] = _("Invalid signup token")
                qcontext['invalid_token'] = True
        return qcontext

    def _prepare_signup_values(self, qcontext):
        res = super(AuthSignupHomeInh, self)._prepare_signup_values(qcontext)
        res.update({key: qcontext.get(key) for key in ('login', 'name', 'password', 'country_id', 'state_id', 'shop',
                                                       'phone', 'mobile', 'street', 'city')})
        if request.params.get('business_registration'):
            res['business_registration'] = base64.b64encode(request.params.get('business_registration').read())
        res['is_company'] = True
        return res

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        value = dict()
        qcontext = kw
        try:
            res = super(AuthSignupHomeInh, self).web_auth_signup(*args, **kw)
            request.update_context(countries=request.env['res.country'].sudo().search([]))
            return res
        except Exception as e:
            user = request.env['res.users'].sudo().search([("login", "=", qcontext.get("login"))])
            if user:
                if user.partner_id:
                    request.env['res.partner'].sudo().create({
                        'name': qcontext.get('contact'), 'type': 'contact', 'parent_id': user.partner_id.id
                    })
                value['error'] = 'User account is created successfully. ' + e.args[0]
            else:
                value['error'] = e.args[0]
            response = request.render('web.login', value)
            response.headers['X-Frame-Options'] = 'SAMEORIGIN'
            response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
            return response
