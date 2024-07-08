import datetime
from odoo import models, api, fields, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round
from odoo.addons.account.models.account_move import AccountMoveLine


class PosOrderReturn(models.Model):
    _inherit = 'pos.order'

    @api.model
    def get_reservation_date(self):
        current_date = datetime.datetime.now()
        reservation = self.env['website.reservation.line'].sudo().search([('date_reserved', '>=', current_date)])
        reservation_list = []
        for i in reservation:
            data = {
                'id': i.id,
                'table': i.reservation_id.name,
                'partner_id': i.partner_id.name or False,
                'phone': i.partner_id.phone or False,
                'email': i.partner_id.email or False,
                'date_reserved': i.date_reserved,
                'seats': i.no_of_people,
                'floor': i.reservation_id.floor_id.name,
                'occasion': i.occasion,
                'request': i.special_request
            }
            reservation_list.append(data)
        return reservation_list
