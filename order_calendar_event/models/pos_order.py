import datetime

from odoo import models, fields, api


class PosOrder(models.Model):
    _inherit = 'pos.order'

    delivery_event_id = fields.Many2one('calendar.event', string='Delivery Event')

    def write(self, vals):
        rec = super(PosOrder, self).write(vals)
        for rec in self:
            try:
                if rec.delivery_type in ['woosh', 'uber', 'door', 'menulog', 'deliveroo', 'swiggy', 'zomato']:
                    prepared_time = (rec.create_date + datetime.timedelta(minutes=rec.preparation_time)) if rec.preparation_time else rec.create_date
                    start_time = rec.delivery_order_time if rec.delivery_order_time else prepared_time
                    if rec.delivery_event_id:
                        event = rec.delivery_event_id
                        event.sudo().write(
                            {'start': start_time, 'stop': start_time + datetime.timedelta(minutes=10)}
                        )
                    else:
                        event = self.env['calendar.event'].sudo().create(
                            {'name': 'Delivery of POS Order: '+rec.pos_reference, 'privacy': 'public', 'show_as': 'free',
                             'start': start_time, 'stop': start_time + datetime.timedelta(minutes=10)}
                        )
                        rec.delivery_event_id = event.id
            except Exception as e:
                pass
        return rec
