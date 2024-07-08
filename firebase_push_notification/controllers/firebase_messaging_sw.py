from odoo import http
from odoo.http import request


class FirebaseReturn(http.Controller):
    @http.route('/firebase-messaging-sw.js', auth='public')
    def create_your_mask(self):
        return request.redirect('/firebase_push_notification/static/src/js/firebase-messaging-sw.js')

    @http.route(['/notification/firebase/info'], type='json', auth="public", website=True)
    def notificationInfoGetM(self, state=None, **kw):
        uid = request.env.user.id
        user = request.env['res.users'].sudo().search([('id', '=', int(uid))], limit=1)
        enable_user = False
        if user:
            enable_user = user.enable_token
        dict = {
            'api_key': request.env['ir.config_parameter'].sudo().get_param('firebase_push_notification.api_key'),
            'authDomain': request.env['ir.config_parameter'].sudo().get_param('firebase_push_notification.authDomain'),
            'projectId': request.env['ir.config_parameter'].sudo().get_param('firebase_push_notification.projectId'),
            'storage_bucket': request.env['ir.config_parameter'].sudo().get_param('firebase_push_notification.storage_bucket'),
            'messaging_senderId': request.env['ir.config_parameter'].sudo().get_param('firebase_push_notification.messaging_senderId'),
            'app_id': request.env['ir.config_parameter'].sudo().get_param('firebase_push_notification.app_id'),
            'enable': request.env['ir.config_parameter'].sudo().get_param('firebase_push_notification.enable'),
            'enable_user': enable_user
        }
        return dict

    @http.route(['/notification/firebase/user/save'], type='json', auth="public", website=True)
    def notificationInfoGetMTokens(self, token=None, **kw):
        uid = request.env.user.id
        if uid and token:
            user = request.env['res.users'].sudo().search([('id', '=', int(uid))], limit=1)
            user.sudo().write({
                'firebase_token':token
            })
            return token
        return False