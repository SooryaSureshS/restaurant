# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo import api, models, fields, _


class WebsiteReservation(http.Controller):
    @http.route(['''/sale/reservation/<int:id>/<string:access_token>/cancel'''], type='http', auth="public", website=True)
    def Cancel_Reservation_mail(self, id=None, access_token=None, **kw):
        if id:
            reservation = request.env['website.reservation.line'].sudo().search([('id', '=', id)], limit=1)
            if reservation.token_random == access_token:
                return request.render('website_reservation.cancel_reservation', {'reservation': reservation})

    @http.route(['''/sale/reservation/<string:token_random>'''], type='http', auth="public", website=True)
    def cancel_reservation(self, id=None, access_token=None, **kw):
        token = kw['token_random']
        if token:
            reservation = request.env['website.reservation.line'].sudo().search([('token_random', '=', token)], limit=1)
            reservation_data = reservation
            message_body = "Hi " + str(reservation_data.partner_id.name) + ", Your table reservation on " + str(reservation_data.date_reserved) + " was cancelled " + "."
            company = request.env.user.company_id
            mail = request.env['mail.mail'].sudo().create({
                'subject': _('Table Reservation Cancelled'),
                'email_from': company.catchall_formatted or company.email_formatted,
                'recipient_ids': [(4, reservation_data.partner_id.id)],
                'body_html': message_body,
            })
            mail.send()
            reservation.unlink()
            return request.render('website_reservation.cancel_reservation_success', {'reservation': True})
