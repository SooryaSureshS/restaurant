from odoo import models, fields


class ResConfigSettingsFpn(models.TransientModel):
    _inherit = 'res.config.settings'

    # apiKey: "AIzaSyDIBiK_BLA0qdMfG9shW4v0UwDSaLCZLBM",
    # authDomain: "skyprodev-cc02b.firebaseapp.com",
    # projectId: "skyprodev-cc02b",
    # storageBucket: "skyprodev-cc02b.appspot.com",
    # messagingSenderId: "321898949292",
    # appId: "1:321898949292:web:f36dc47fdf74d1ccf20d09"

    api_key = fields.Char()
    authDomain = fields.Char()
    projectId = fields.Char()
    storage_bucket = fields.Char()
    messaging_senderId = fields.Char()
    app_id = fields.Char()
    serverToken = fields.Char()
    enable = fields.Boolean()
    # website_id = fields.Char()


    def get_values(self):
        res = super(ResConfigSettingsFpn, self).get_values()
        res.update(
            api_key=self.env['ir.config_parameter'].sudo().get_param('firebase_push_notification.api_key'),
            authDomain=self.env['ir.config_parameter'].sudo().get_param('firebase_push_notification.authDomain'),
            projectId=self.env['ir.config_parameter'].sudo().get_param('firebase_push_notification.projectId'),
            storage_bucket=self.env['ir.config_parameter'].sudo().get_param('firebase_push_notification.storage_bucket'),
            messaging_senderId=self.env['ir.config_parameter'].sudo().get_param('firebase_push_notification.messaging_senderId'),
            app_id=self.env['ir.config_parameter'].sudo().get_param('firebase_push_notification.app_id'),
            serverToken=self.env['ir.config_parameter'].sudo().get_param('firebase_push_notification.serverToken'),
            enable=self.env['ir.config_parameter'].sudo().get_param('firebase_push_notification.enable'),
        )
        return res

    def set_values(self):
        super(ResConfigSettingsFpn, self).set_values()
        param = self.env['ir.config_parameter'].sudo()


        api_key = self.api_key
        authDomain = self.authDomain
        projectId = self.projectId
        storage_bucket = self.storage_bucket
        messaging_senderId = self.messaging_senderId
        app_id = self.app_id
        serverToken = self.serverToken
        enable = self.enable


        param.set_param('firebase_push_notification.api_key', api_key)
        param.set_param('firebase_push_notification.authDomain', authDomain)
        param.set_param('firebase_push_notification.projectId', projectId)
        param.set_param('firebase_push_notification.storage_bucket', storage_bucket)
        param.set_param('firebase_push_notification.messaging_senderId', messaging_senderId)
        param.set_param('firebase_push_notification.app_id', app_id)
        param.set_param('firebase_push_notification.serverToken', serverToken)
        param.set_param('firebase_push_notification.enable', enable)



