from odoo import http
import json
from odoo.http import request
import threading
import odoo


def get_db_name():
    db = odoo.tools.config['db_name']
    if not db and hasattr(threading.current_thread(), 'dbname'):
        return threading.current_thread().dbname
    return db


class PropertyManagementApi(http.Controller):

    @http.route('/user/register', type='json', auth="public", methods=['POST', 'GET'], csrf=False)
    def user_register(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            if data.get('email'):
                if request.env['res.partner'].sudo().search([('email', '=', data.get('email'))]):
                    return {
                        'status': 0,
                        'message': "The given email is already registered"
                    }
                else:
                    partner = request.env['res.partner'].sudo().create(
                        {'name': f"{data.get('first_name')} {data.get('last_name')}",
                         'email': data.get('email'),
                         'mobile': data.get('mobile')
                         })
                    group_portal_user = request.env.ref('base.group_portal')
                    user = request.env['res.users'].sudo().create({
                        'company_id': request.env.company.id,
                        'email': data.get('email'),
                        'name': f"{data.get('first_name')} {data.get('last_name')}",
                        'login': data.get('email'),
                        'partner_id': partner.id,
                        'new_password': data.get('password'),
                        'groups_id': [(6, 0, [group_portal_user.id])],
                        'totp_enabled': True
                    })
                    if user:
                        user.write({'password': data.get('password'), 'new_password': data.get('password')})
                        partner.write({'user_id': user.id})

                        return {'success': True,
                                'user_id': user.id,
                                'name': f"{data.get('first_name')} {data.get('last_name')}",
                                'first_name': data.get('first_name'),
                                'last_name': data.get('last_name'),
                                'email': data.get('email'),
                                'mobile': data.get('mobile'),
                                'message': "User Registered"
                                }

        except Exception as e:
            return {
                'status': 0,
                'message': e
            }

    def generateOTP(self):
        import secrets
        secrets_generator = secrets.SystemRandom()
        otp = secrets_generator.randint(100000, 999999)
        return otp

    @http.route('/forgot/password', type='json', auth="public", methods=['POST', 'GET'], csrf=False)
    def forgot_password(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            email = data.get('email')
            if email:
                user = request.env['res.users'].sudo().search([('email', '=', email)])
                if user:
                    otp = self.generateOTP()
                    body_html = '''<div style="margin: 0px; padding: 0px;">
                                  <p style="margin: 0px; padding: 0px; font-size: 13px;">
                                      Hi ''' + user.name + ''',
                                      <br/><br/>
                                       <p>
                                          Please find the OTP number ''' + str(otp) + ''' for your password reset
                                          <br/><br/>
                                      Thank you
                                  </p>
                              </div>'''
                    mail = request.env['ir.mail_server'].sudo().search([], limit=1)
                    mail_from = mail.smtp_user
                    template_obj = request.env['mail.mail'].sudo().search([], limit=1)
                    template_data = {
                        'subject': 'Password Reset OTP',
                        'body_html': body_html,
                        'email_from': mail_from,
                        'email_to': user.email
                    }
                    template_id = template_obj.create(template_data)
                    template_id.sudo().send()
                    user.write({
                        'user_otp': otp
                    })
                    return {'success': True, 'otp': otp, 'message': "Password reset mail sent"}

                return {
                    'status': 0,
                    'message': "Email doesn't exist"
                }
        except Exception as e:
            return {
                'status': 0,
                'message': e
            }

    @http.route('/forgot/password/verify', type='json', auth="public", methods=['POST'], csrf=False)
    def forgot_password_verify(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            email_id = data.get('email')
            otp = data.get('otp')
            if email_id and otp:
                user_id = request.env['res.users'].sudo().search([('email', '=', email_id), ('user_otp', '=', otp)])
                if user_id:
                    return {'success': True, 'message': "OTP Verified"}
                else:
                    return {
                        'status': 0,
                        'message': "OTP/Email you have entered is incorrect"
                    }
            return {
                'status': 0,
                'message': "Email doesn't registered or exist"
            }
        except Exception as e:
            return {
                'status': 0,
                'message': "Email doesn't registered or exist"
            }

    def _set_encrypted_password(self, uid, pw):
        assert self._crypt_context().identify(pw) != 'plaintext'

        self.env.cr.execute(
            'UPDATE res_users SET password=%s WHERE id=%s',
            (pw, uid)
        )
        self.invalidate_cache(['password'], [uid])

    @http.route('/reset/password', type='json', auth="public", methods=['POST'], csrf=False)
    def reset_password(self):
        import passlib
        ctx = passlib.context.CryptContext(
            ['pbkdf2_sha512', 'plaintext'],
            deprecated=['plaintext'],
        )
        try:
            data = request.httprequest.data
            data = json.loads(data)
            email_id = data.get('email')
            password = data.get('password')
            confirmed_password = data.get('confirmed_password')
            if password == confirmed_password:
                user_id = request.env['res.users'].sudo().search([('email', '=', email_id)])
                if user_id:
                    hash_password = ctx.hash if hasattr(ctx, 'hash') else ctx.encrypt
                    user_id._set_encrypted_password(user_id.id, hash_password(confirmed_password))
                    user_id.user_otp = ""
                    return {'success': True, 'message': "New Password has been reset"}
                else:
                    return {
                        'status': 0,
                        'message': "Passwords are not match"
                    }
            return {
                'status': 0,
                'message': "Passwords are not match"
            }
        except Exception as e:
            return {
                'status': 0,
                'message': "Passwords are not match"
            }

    @http.route('/user/login', type='json', auth="public", methods=['POST'])
    def user_authenticate(self):
        try:
            data = request.httprequest.data
            data = json.loads(data)
            db = get_db_name()
            uid = request.session.authenticate(db, data.get('email', False),
                                               data.get('password', False))
            user_obj = request.env['res.users'].sudo().search([('id', '=', uid)])
            user_details = {'success': True,
                            'user_id': uid,
                            'customer_id': user_obj.partner_id.id}
            return user_details
        except Exception as e:
            return {
                'status': 0,
                'message': "The given user name or password is wrong"
            }

    @http.route('/property/home', type='json', auth="user", methods=['POST'])
    def property_home_page(self):
        popular_properties = request.env['product.product'].sudo().search([('is_property', '=', True)],
                                                                          order='id DESC')
        popular_properties_list = []
        for product in popular_properties:
            most_ordered_dict = {
                'property_id': product.id,
                'property_image': product.image_1920,
            }
            popular_properties_list.append(most_ordered_dict)
        return popular_properties_list

    @http.route('/property/to_sell', type='json', auth="user", methods=['POST'])
    def property_to_sell(self):
        properties_to_sell = request.env['product.product'].sudo().search_read([('property_book_for', '=', 'sale'),
                                                                                ('state', '=', 'sale'),
                                                                                ('is_sold', '=', False)])
        return properties_to_sell

    @http.route('/property/to_rent', type='json', auth="user", methods=['POST'])
    def property_to_rent(self):
        properties_to_rent = request.env['product.product'].sudo().search_read([('property_book_for', '=', 'rent'),
                                                                                ('state', '=', 'rent'),
                                                                                ('rent_unit', '=', 'monthly'),
                                                                                ('is_reserved', '=', False)])
        return properties_to_rent

    @http.route('/property/to_lease', type='json', auth="user", methods=['POST'])
    def property_to_lease(self):
        properties_to_lease = request.env['product.product'].sudo().search_read([('property_book_for', '=', 'rent'),
                                                                                 ('state', '=', 'rent'),
                                                                                 ('rent_unit', '=', 'yearly'),
                                                                                 ('is_reserved', '=', False)])
        return properties_to_lease

    @http.route('/property/detail', type='json', auth="user", methods=['POST'])
    def property_detail(self):
        data = request.httprequest.data
        data = json.loads(data)
        property = request.env['product.product'].search_read([('id', '=', data.get('property_id'))])
        return property
