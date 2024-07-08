from odoo import models, fields, api,_
import logging
_logger = logging.getLogger(__name__)
from datetime import datetime, date, timedelta
import pytz
from pytz import timezone





class WebsiteReservation(models.Model):
    _inherit = 'restaurant.table'

    current_status = fields.Selection([('reserved_30', 'Have reservation in less than 30 min'), ('reserved_15', 'Reservation will end less than in 15 min'), ('reserved', 'Reserved'), ('reserved', 'Reserved'),('available', 'Available')], compute='check_current_status')


    @api.depends('book_date')
    def check_current_status(self):
        if self.book_date:
            current_company= self.env.company
            tz = pytz.timezone(current_company.tz)
            now = datetime.utcnow()
            curret_time = datetime.now()
            curret_time_15 = curret_time + timedelta(minutes=15)
            curret_time_30 = curret_time + timedelta(minutes=30)
            booking = self.book_date.search([('date_reserved', '<=', curret_time), ('date_reserved_end', '>=', curret_time)])

            if booking:
                booking_15 = self.book_date.search([('date_reserved_end', '<=', curret_time_15),('date_reserved', '<=', curret_time), ('date_reserved_end', '>=', curret_time)])
                if booking_15:
                    self.current_status = 'reserved_15'
                else:
                    self.current_status = 'reserved'
            else:
                booking_30 = self.book_date.search(
                    [('date_reserved', '<=', curret_time_30), ('date_reserved_end', '>=', curret_time_30)])
                if booking_30:
                    self.current_status = 'reserved_30'
                else:
                    self.current_status = 'available'
        else:
            self.current_status = 'available'
