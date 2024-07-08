from odoo import models, fields, api, _
from datetime import datetime
import datetime
import datetime as Datetime
from datetime import datetime
import pytz
from dateutil.relativedelta import relativedelta
from pytz import timezone
from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)


class PosConfigParamsBooking(models.Model):
    _inherit = 'pos.config'

    enable_table_booking = fields.Boolean('Enable Table Booking')
    table_available_color = fields.Char(string="Table Available Color",help="Choose your color")
    table_unavailable_color = fields.Char(string="Table Unavailable Color",help="Choose your color")
    table_unavailable_soon_color = fields.Char(string="Table Unavailable Soon Color",help="Choose your color")
    table_available_soon_color = fields.Char(string="Table Available Soon Color",help="Choose your color")
    minimize_booking_gape = fields.Integer(string="Booking Gape In min", default=15)
    booking_time_out = fields.Integer(string="Booking Time Out", default=15)
    soon_available = fields.Integer(string="Soon become available", default=15)

    def get_tables_order_count(self):
        """         """
        print("\n _____get_tables_order_count____\n")
        self.ensure_one()
        tables = self.env['restaurant.table'].search([('floor_id.pos_config_id', 'in', self.ids)])
        domain = [('state', '=', 'draft'), ('table_id', 'in', tables.ids), ('lines', '!=', False)]

        order_stats = self.env['pos.order'].read_group(domain, ['table_id'], 'table_id')
        orders_map = dict((s['table_id'][0], s['table_id_count']) for s in order_stats)
        result = []
        for table in tables:
            result.append({'id': table.id, 'orders': orders_map.get(table.id, 0)})
        return result

    @api.model
    def get_tables_reservation_available(self,config,minimize_booking_gape ):
        """         """
        # self.ensure_one()
        print("\n _____-get_tables_reservation_available_______\n")
        unavailable_tables_list = []
        soon_unavailable_tables_list = []
        soon_available_tables_list = []
        res_config_settings = self.env['ir.config_parameter'].sudo()
        pos_config = self.env['pos.config'].sudo().search([('id', '=', int(config))], limit=1)
        reservation_time = res_config_settings.get_param('website_reservation.reservation_time')
        current = self.env.company
        tz = pytz.timezone(current.tz)
        now = datetime.utcnow()
        utc = timezone('UTC')
        utc.localize(datetime.now())
        delta = utc.localize(now) - tz.localize(now)
        time_soon_gap = float(minimize_booking_gape) + float(reservation_time)
        time_ends = now - relativedelta(minutes=float(time_soon_gap))
        started_order = self.current_order_staus_update()
        if reservation_time and minimize_booking_gape and config:
            unavailable_tables = self.env['website.reservation.line'].sudo().search([('date_reserved_end','>=',now),('date_reserved','<=',now),('state','!=','cancel')])
            for i in unavailable_tables:
                time_elapse = i.date_reserved - time_ends
                sec = time_elapse.seconds
                total_minute = sec / 60
                end_time_lapse = i.date_reserved_end - now
                seconds_lapse = end_time_lapse.seconds
                total_minute_lapse = seconds_lapse / 60
                time_lapsed_red = False
                if str(total_minute_lapse).split('.')[0]:
                    time_lapsed_red = str(total_minute_lapse).split('.')[0]+'m'
                if str(total_minute_lapse).split('.')[1]:
                    time_lapsed_red = time_lapsed_red + "{:.2f}".format(total_minute_lapse).split('.')[1] + 's'
                merged_table = i.merged_table.id
                if total_minute <= time_soon_gap:
                    dict_rev = {
                        'table_id': i.reservation_id.id,
                        'table_name': i.reservation_id.name,
                        'date_reserved': i.date_reserved.astimezone(tz),
                        'date_reserved_end': i.date_reserved_end.astimezone(tz),
                        'occasion': i.occasion,
                        'special_request': i.special_request,
                        'partner_id': i.partner_id.name,
                        'id': i.id,
                        'state': i.state,
                        'name': i.name,
                        'started_order': started_order,
                        'end_time_lapse': str(time_lapsed_red),
                        'merged_table': merged_table,
                        'border_color': i.border_color,
                    }
                    unavailable_tables_list.append(dict_rev)
            time_soon_gap1 = float(minimize_booking_gape)

            soon_unavailable= self.env['website.reservation.line'].sudo().search([('date_reserved', '>', now),('state','!=','cancel')])
            for i in soon_unavailable:
                time_date_reserved = i.date_reserved-now
                sec1 = time_date_reserved.seconds
                total_minute1 = sec1 / 60
                merged_table = i.merged_table.id
                if total_minute1 < time_soon_gap1 and total_minute1 > 0:
                    dict_rev = {
                        'table_id': i.reservation_id.id,
                        'table_name': i.reservation_id.name,
                        'date_reserved': i.date_reserved.astimezone(tz),
                        'date_reserved_end': i.date_reserved_end.astimezone(tz),
                        'occasion': i.occasion,
                        'special_request': i.special_request,
                        'partner_id': i.partner_id.name,
                        'id': i.id,
                        'state': i.state,
                        'name': i.name,
                        'merged_table': merged_table,
                        'border_color': i.border_color,
                    }
                    soon_unavailable_tables_list.append(dict_rev)
            time_soon_gap3 = float(minimize_booking_gape)
            time_ends3 = now + relativedelta(minutes=float(time_soon_gap3))
            # soon_available_tables = self.env['website.reservation.line'].sudo().search([('date_reserved_end','<', now + relativedelta(minutes=float(reservation_time))),('date_reserved_end','>', now - relativedelta(minutes=float(reservation_time)))])
            soon_available_tables = self.env['website.reservation.line'].sudo().search([('date_reserved_end','>', now),('state','!=','cancel')])
            for i in soon_available_tables:
                time_date_reserved3 = i.date_reserved_end - now
                sec1 = time_date_reserved3.seconds
                total_minute3 = sec1 / 60
                merged_table = i.merged_table.id
                if total_minute3 > 0 and  total_minute3 <= pos_config.soon_available and total_minute3>0:
                    time_soon_gap = float(minimize_booking_gape) + float(reservation_time)
                    check = i.date_reserved_end + relativedelta(minutes=float(time_soon_gap))
                    next_reservation = self.env['website.reservation.line'].sudo().search(
                        [('reservation_id', '=', i.reservation_id.id), ('date_reserved', '>', now),
                         ('date_reserved', '<', check), ('state', '!=', 'cancel')])
                    if next_reservation:
                        pass
                    else:
                        dict_rev = {
                            'table_id': i.reservation_id.id,
                            'table_name': i.reservation_id.name,
                            'date_reserved': i.date_reserved.astimezone(tz),
                            'date_reserved_end': i.date_reserved_end.astimezone(tz),
                            'occasion': i.occasion,
                            'special_request': i.special_request,
                            'partner_id': i.partner_id.name,
                            'id': i.id,
                            'state': i.state,
                            'name': i.name,
                            'merged_table': merged_table,
                            'border_color': i.border_color,
                        }
                        soon_available_tables_list.append(dict_rev)


        return [unavailable_tables_list,soon_unavailable_tables_list,soon_available_tables_list]

    def current_order_staus_update(self):
        now = datetime.utcnow()
        current_table_orders = self.env['website.reservation.line'].sudo().search([('date_reserved', '<', now),('date_reserved_end', '>', now)])
        order_list = []
        red_signal = []
        start_signal = []
        state = False
        for res in current_table_orders:
            pos_orders = self.env['pos.order'].sudo().search([('date_order', '>', res.date_reserved),('reservation','=',res.id)],order='id desc', limit=1)
            for i in pos_orders:
                for j in i.lines:
                    state = j.order_line_state
                time_rem = i.date_order + relativedelta(minutes=float(i.preparation_time))
                time_lapsed_red = False
                if time_rem > now:
                    time_remains_for_delivery = time_rem - now
                    sec_rem = time_remains_for_delivery.seconds
                    time_remains_for_delivery_min = sec_rem / 60
                    time_lapsed_red = False
                    if str(time_remains_for_delivery_min).split('.')[0]:
                        time_lapsed_red = str(time_remains_for_delivery_min).split('.')[0]+'m'
                    if str(time_remains_for_delivery_min).split('.')[1]:
                        time_lapsed_red = time_lapsed_red + "{:.2f}".format(time_remains_for_delivery_min).split('.')[1] + 's'
                start_signal_dict = {
                    'table_id': res.reservation_id.id,
                    'create_date': i.create_date,
                    'preparation_time': i.preparation_time,
                    'perparation_elapse': time_lapsed_red,
                    'state': state,
                    'name': i.name,
                    'id': i.id,
                }
                start_signal.append(start_signal_dict)
        print("\n _____-start_signal_______",start_signal)
        return [start_signal]


    @api.model
    def table_exits(self,booking_selected_table,booking_date,select_time ):
        booking_date = booking_date.replace('-', '/')
        current = request.env.company
        tz = pytz.timezone(current.tz)
        booking_date = datetime.strptime(booking_date, '%Y/%m/%d').date()
        time_val = datetime.strptime(select_time, '%H:%M').time()
        start_time = datetime.combine(booking_date, time_val).astimezone(tz)

class PosConfigFloorConfigTable(models.Model):
    _inherit = 'restaurant.table'

    background_color = fields.Char(string="Table Color",help="Choose your color")
    # current_status = fields.Selection([('reserved_30', 'Have reservation in less than 30 min'), ('reserved_15', 'Reservation will end less than in 15 min'), ('reserved', 'Reserved'), ('reserved', 'Reserved'),('available', 'Available')], compute='check_current_status')


class PosConfigTableReservationsTable(models.Model):
    _inherit = 'website.reservation.line'

    # background_color = fields.Char(string="Table Color", help="Choose your color")
    state = fields.Selection(selection=[("waiting", "Waiting"),
                                       ("ready", "Ready"),
                                       ("done", "Done"),
                                       ("cancel", "Cancel")], default="waiting")
    merged_table = fields.Many2one('restaurant.table', string="Merged Table", help="Choose your color")
    border_color = fields.Char(string="Table Color",help="Choose your color")



class PosReservationConnection(models.Model):

    _inherit = 'pos.order'

    reservation = fields.Many2one('website.reservation.line')
    people_number = fields.Integer('Number of people')


    def _order_fields(self, ui_order):
        order = super(PosReservationConnection, self)._order_fields(ui_order)
        if 'reservation' in ui_order.keys() and ui_order['reservation']:
            order['reservation'] = ui_order['reservation']
        return order

    def set_people_number(self, order_id, people_number):
        order_obj = self.env['pos.order'].sudo().search([('pos_reference', '=', order_id)], limit=1)
        if order_obj:
            order_obj.people_number = people_number


# ======================= Add 14 May ===================================================
import pytz
_tzs = [(tz, tz) for tz in sorted(pytz.all_timezones, key=lambda tz: tz if not tz.startswith('Etc/') else '_')]


def _tz_get(self):
    return _tzs


class ResCompany(models.Model):
    _inherit = 'res.company'

    tz = fields.Selection(_tz_get, string='Timezone', default=lambda self: self._context.get('tz'),
        help="When printing documents and exporting/importing data, "
            "time values are computed according to this timezone.\n"
            "If the timezone is not set, UTC (Coordinated Universal Time) is used.\n"
            "Anywhere else, time values are computed according to the time offset of your web client.")

    tz_offset = fields.Char(compute='_compute_tz_offset', string='Timezone offset', invisible=True)

# ------------------------------------------------------------------------------------------------