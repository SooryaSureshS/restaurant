# -*- coding: utf-8 -*-

from odoo import models, fields, api


class automatic_session_close(models.Model):
    _name = 'automatic_session_close.automatic_session_close'
    _description = 'automatic_session_close.automatic_session_close'

    name = fields.Char()
    create_date = fields.Datetime()
    description = fields.Text()


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _auto_session_close(self):
        log = self.env['automatic_session_close.automatic_session_close']
        sessions = self.sudo().search([('state','in',['opened', 'closing_control'])])
        for rec in sessions:
            try:
                rec.action_pos_session_closing_control()
                rec.action_pos_session_validate()
            except Exception as e:
                log.sudo().create({'name':'Session Close','create_date':fields.Datetime.now(),
                                   'description':str(e)
                                   })


