from odoo import models, fields, api
import random


class WebsiteReservation(models.Model):
    _inherit = 'restaurant.table'

    book_date = fields.One2many('website.reservation.line', 'reservation_id')


class SaleConfig(models.TransientModel):
    _inherit = 'res.config.settings'
    reservation_time = fields.Float('Table Reservation Time', default=60.00)

    def get_values(self):
        res = super(SaleConfig, self).get_values()

        # Website Sale Day timings
        res.update(
            reservation_time=self.env['ir.config_parameter'].sudo().get_param(
                'website_reservation.reservation_time'),
        )
        return res

    def set_values(self):
        super(SaleConfig, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        reservation_time = self.reservation_time

        param.set_param('website_reservation.reservation_time', reservation_time)


class WebsiteReservationLine(models.Model):
    _name = 'website.reservation.line'

    reservation_id = fields.Many2one('restaurant.table')
    date_reserved = fields.Datetime()
    date_reserved_end = fields.Datetime()
    no_of_people = fields.Integer(string='Seats')
    occasion = fields.Selection([('birthday', 'Birthday'), ('date', 'Date'),
                                 ('business', 'Business Meal'), ('special', 'Special Occasion')],
                                string="Occasion")
    special_request = fields.Char(string="Special Request")
    partner_id = fields.Many2one('res.partner')
    token_random = fields.Char()
    company_id = fields.Many2one(
        'res.company', 'Company', default=lambda self: self.env.company,
        index=True, readonly=True, required=True,
        help='The company is automatically set from your user preferences.')

    def create(self, values):
        reservation = super(WebsiteReservationLine, self).create(values)
        # mail_template = self.env.ref('website_reservation.mail_template_table_reservation')
        # mail_template.send_mail(reservation.id, force_send=True)
        return reservation

    def cancel_reservation(self):
        """Create portal url for user to update the scheduled date on purchase
        order lines."""
        if not self.token_random:
            sample_string = 'pqrstuvwxy'
            result = ''.join((random.choice(sample_string)) for x in range(50))
            self.token_random = result
        update_param = '/sale/reservation' + '/' + str(self.id) + '/' + str(self.token_random) + '/cancel'
        return update_param
