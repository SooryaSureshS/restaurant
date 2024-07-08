from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleTimeAndDay(models.Model):
    _name = 'sale.day'

    day_name = fields.Char()
    day = fields.Selection([('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'),
                            ('3', 'Thursday'), ('4', 'Friday'), ('5', 'Saturday'), ('6', 'Sunday')])
    time_from = fields.Float('From')
    time_to = fields.Float('to')


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    hour_website = fields.Boolean()


class SaleConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    sunday_from = fields.Float('Sunday From')
    sunday_to = fields.Float('Sunday To')

    monday_from = fields.Float('Monday From')
    monday_to = fields.Float('Monday To')

    tuesday_from = fields.Float('Tuesday From')
    tuesday_to = fields.Float('Tuesday To')

    wednesday_from = fields.Float('Wednesday From')
    wednesday_to = fields.Float('Wednesday To')

    thursday_from = fields.Float('Thursday From')
    thursday_to = fields.Float('Thursday To')

    friday_from = fields.Float('Friday From')
    friday_to = fields.Float('Friday To')

    saturday_from = fields.Float('Saturday From')
    saturday_to = fields.Float('Saturday To')

    pickup_time = fields.Float("Pickup Time", digits=(16, 2))
    delivery_time = fields.Float("Delivery Time", digits=(16, 2))

    time_from_pickup_sunday = fields.Float('From')
    time_to_pickup_sunday = fields.Float('To')

    time_from_pickup_monday = fields.Float('From')
    time_to_pickup_monday = fields.Float('To')

    time_from_pickup_tuesday = fields.Float('From')
    time_to_pickup_tuesday = fields.Float('To')

    time_from_pickup_wednesday = fields.Float('From')
    time_to_pickup_wednesday = fields.Float('To')

    time_from_pickup_thursday = fields.Float('From')
    time_to_pickup_thursday = fields.Float('To')

    time_from_pickup_friday = fields.Float('From')
    time_to_pickup_friday = fields.Float('To')

    time_from_pickup_saturday = fields.Float('From')
    time_to_pickup_saturday = fields.Float('To')

    # Delivery Timing

    time_from_delivery_sunday = fields.Float('From')
    time_to_delivery_sunday = fields.Float('To')

    time_from_delivery_monday = fields.Float('From')
    time_to_delivery_monday = fields.Float('To')

    time_from_delivery_tuesday = fields.Float('From')
    time_to_delivery_tuesday = fields.Float('To')

    time_from_delivery_wednesday = fields.Float('From')
    time_to_delivery_wednesday = fields.Float('To')

    time_from_delivery_thursday = fields.Float('From')
    time_to_delivery_thursday = fields.Float('To')

    time_from_delivery_friday = fields.Float('From')
    time_to_delivery_friday = fields.Float('To')

    time_from_delivery_saturday = fields.Float('From')
    time_to_delivery_saturday = fields.Float('To')

    future_order_from = fields.Integer("From")
    future_order_from_type = fields.Selection([('minute', 'Minutes'), ('hour', 'Hours'), ('day', 'Days')])
    future_order_to = fields.Integer("TO")
    future_order_to_type = fields.Selection([('minute', 'Minutes'), ('hour', 'Hours'), ('day', 'Days')])

    curb_side_pickup = fields.Boolean("Kerbside Pick-UP")
    website_delivery = fields.Boolean("Website Delivery")
    pre_order_kitchen_display = fields.Float('Pre Orders Kitchen Display Time')
    pos_order_kitchen_display = fields.Float('POS Orders Kitchen Display Time')

    def get_values(self):
        res = super(SaleConfig, self).get_values()

        # Website Sale Day timings
        res.update(
            sunday_from=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.sunday_from'),
        )

        res.update(
            sunday_to=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.sunday_to'),
        )

        res.update(
            monday_from=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.monday_from'),
        )

        res.update(
            monday_to=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.monday_to'),
        )

        res.update(
            tuesday_from=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.tuesday_from'),
        )

        res.update(
            tuesday_to=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.tuesday_to'),
        )

        res.update(
            wednesday_from=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.wednesday_from'),
        )

        res.update(
            wednesday_to=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.wednesday_to'),
        )

        res.update(
            thursday_from=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.thursday_from'),
        )

        res.update(
            thursday_to=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.thursday_to'),
        )

        res.update(
            friday_from=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.friday_from'),
        )

        res.update(
            friday_to=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.friday_to'),
        )

        res.update(
            saturday_from=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.saturday_from'),
        )

        res.update(
            saturday_to=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.saturday_to'),
        )

        # Minimum PickupTime
        res.update(
            pickup_time=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.pickup_time'),
        )

        # Website Delivery Time
        res.update(
            delivery_time=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.delivery_time'),
        )

        res.update(
            future_order_from=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.future_order_from'),
        )
        res.update(
            future_order_to=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.future_order_to'),
        )
        res.update(
            future_order_from_type=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.future_order_from_type'),
        )
        res.update(
            future_order_to_type=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.future_order_to_type'),
        )

        # curb_side_pickup
        res.update(
            curb_side_pickup=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.curb_side_pickup'),
        )
        # website_delivery
        res.update(
            website_delivery=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.website_delivery'),
        )

        # picking time
        res.update(
            time_from_pickup_sunday=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.time_from_pickup_sunday'),
        )
        res.update(
            time_to_pickup_sunday=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.time_to_pickup_sunday'),
        )
        res.update(
            time_from_pickup_monday=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.time_from_pickup_monday'),
        )
        res.update(
            time_to_pickup_monday=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.time_to_pickup_monday'),
        )
        res.update(
            time_from_pickup_tuesday=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.time_from_pickup_tuesday'),
        )
        res.update(
            time_to_pickup_tuesday=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.time_to_pickup_tuesday'),
        )
        res.update(
            time_from_pickup_wednesday=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.time_from_pickup_wednesday'),
        )
        res.update(
            time_to_pickup_wednesday=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.time_to_pickup_wednesday'),
        )

        res.update(
            time_from_pickup_thursday=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.time_from_pickup_thursday'),
        )
        res.update(
            time_to_pickup_thursday=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.time_to_pickup_thursday'),
        )

        res.update(
            time_from_pickup_friday=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.time_from_pickup_friday'),
        )
        res.update(
            time_to_pickup_friday=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.time_to_pickup_friday'),
        )

        res.update(
            time_from_pickup_saturday=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.time_from_pickup_saturday'),
        )
        res.update(
            time_to_pickup_saturday=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.time_to_pickup_saturday'),
        )

        # Delivery Time range
        res.update(
            time_from_delivery_sunday=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.time_from_delivery_sunday'),
        )
        res.update(
            time_to_delivery_sunday=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.time_to_delivery_sunday'),
        )
        res.update(
            time_from_delivery_monday=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.time_from_delivery_monday'),
        )
        res.update(
            time_to_delivery_monday=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.time_to_delivery_monday'),
        )
        res.update(
            time_from_delivery_tuesday=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.time_from_delivery_tuesday'),
        )
        res.update(
            time_to_delivery_tuesday=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.time_to_delivery_tuesday'),
        )
        res.update(
            time_from_delivery_wednesday=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.time_from_delivery_wednesday'),
        )
        res.update(
            time_to_delivery_wednesday=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.time_to_delivery_wednesday'),
        )

        res.update(
            time_from_delivery_thursday=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.time_from_delivery_thursday'),
        )
        res.update(
            time_to_delivery_thursday=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.time_to_delivery_thursday'),
        )

        res.update(
            time_from_delivery_friday=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.time_from_delivery_friday'),
        )
        res.update(
            time_to_delivery_friday=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.time_to_delivery_friday'),
        )

        res.update(
            time_from_delivery_saturday=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.time_from_delivery_saturday'),
        )
        res.update(
            time_to_delivery_saturday=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.time_to_delivery_saturday'),
        )

        res.update(
            pre_order_kitchen_display=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.pre_order_kitchen_display'),
        )
        res.update(
            pos_order_kitchen_display=self.env['ir.config_parameter'].sudo().get_param(
                'website_sale_hour.pos_order_kitchen_display'),
        )

        return res

    def set_values(self):
        super(SaleConfig, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        # Website Sale Day timings
        sunday_from = self.sunday_from
        sunday_to = self.sunday_to
        monday_from = self.monday_from
        monday_to = self.monday_to
        tuesday_from = self.tuesday_from
        tuesday_to = self.tuesday_to
        wednesday_from = self.wednesday_from
        wednesday_to = self.wednesday_to
        thursday_from = self.thursday_from
        thursday_to = self.thursday_to
        friday_from = self.friday_from
        friday_to = self.friday_to
        saturday_from = self.saturday_from
        saturday_to = self.saturday_to

        pickup_time = self.pickup_time
        delivery_time = self.delivery_time

        future_order_from = self.future_order_from
        future_order_to = self.future_order_to
        future_order_from_type = self.future_order_from_type
        future_order_to_type = self.future_order_to_type

        curb_side_pickup = self.curb_side_pickup
        website_delivery = self.website_delivery

        time_from_pickup_sunday = self.time_from_pickup_sunday
        time_to_pickup_sunday = self.time_to_pickup_sunday

        time_from_pickup_monday = self.time_from_pickup_monday
        time_to_pickup_monday = self.time_to_pickup_monday

        time_from_pickup_tuesday = self.time_from_pickup_tuesday
        time_to_pickup_tuesday = self.time_to_pickup_tuesday

        time_from_pickup_wednesday = self.time_from_pickup_wednesday
        time_to_pickup_wednesday = self.time_to_pickup_wednesday

        time_from_pickup_thursday = self.time_from_pickup_thursday
        time_to_pickup_thursday = self.time_to_pickup_thursday

        time_from_pickup_friday = self.time_from_pickup_friday
        time_to_pickup_friday = self.time_to_pickup_friday

        time_from_pickup_saturday = self.time_from_pickup_saturday
        time_to_pickup_saturday = self.time_to_pickup_saturday

        time_from_delivery_sunday = self.time_from_delivery_sunday
        time_to_delivery_sunday = self.time_to_delivery_sunday

        time_from_delivery_monday = self.time_from_delivery_monday
        time_to_delivery_monday = self.time_to_delivery_monday

        time_from_delivery_tuesday = self.time_from_delivery_tuesday
        time_to_delivery_tuesday = self.time_to_delivery_tuesday

        time_from_delivery_wednesday = self.time_from_delivery_wednesday
        time_to_delivery_wednesday = self.time_to_delivery_wednesday

        time_from_delivery_thursday = self.time_from_delivery_thursday
        time_to_delivery_thursday = self.time_to_delivery_thursday

        time_from_delivery_friday = self.time_from_delivery_friday
        time_to_delivery_friday = self.time_to_delivery_friday

        time_from_delivery_saturday = self.time_from_delivery_saturday
        time_to_delivery_saturday = self.time_to_delivery_saturday

        pre_order_kitchen_display = self.pre_order_kitchen_display
        pos_order_kitchen_display = self.pos_order_kitchen_display

        param.set_param('website_sale_hour.sunday_from', sunday_from)
        param.set_param('website_sale_hour.sunday_to', sunday_to)
        param.set_param('website_sale_hour.monday_from', monday_from)
        param.set_param('website_sale_hour.monday_to', monday_to)
        param.set_param('website_sale_hour.tuesday_from', tuesday_from)
        param.set_param('website_sale_hour.tuesday_to', tuesday_to)
        param.set_param('website_sale_hour.wednesday_from', wednesday_from)
        param.set_param('website_sale_hour.wednesday_to', wednesday_to)
        param.set_param('website_sale_hour.thursday_from', thursday_from)
        param.set_param('website_sale_hour.thursday_to', thursday_to)
        param.set_param('website_sale_hour.friday_from', friday_from)
        param.set_param('website_sale_hour.friday_to', friday_to)
        param.set_param('website_sale_hour.saturday_from', saturday_from)
        param.set_param('website_sale_hour.saturday_to', saturday_to)

        param.set_param('website_sale_hour.pickup_time', pickup_time)
        param.set_param('website_sale_hour.delivery_time', delivery_time)

        param.set_param('website_sale_hour.future_order_from', future_order_from)
        param.set_param('website_sale_hour.future_order_to', future_order_to)
        param.set_param('website_sale_hour.future_order_from_type', future_order_from_type)
        param.set_param('website_sale_hour.future_order_to_type', future_order_to_type)

        param.set_param('website_sale_hour.curb_side_pickup', curb_side_pickup)
        param.set_param('website_sale_hour.website_delivery', website_delivery)

        # Pickup Timings
        param.set_param('website_sale_hour.time_from_pickup_sunday', time_from_pickup_sunday)
        param.set_param('website_sale_hour.time_to_pickup_sunday', time_to_pickup_sunday)

        param.set_param('website_sale_hour.time_from_pickup_monday', time_from_pickup_monday)
        param.set_param('website_sale_hour.time_to_pickup_monday', time_to_pickup_monday)

        param.set_param('website_sale_hour.time_from_pickup_tuesday', time_from_pickup_tuesday)
        param.set_param('website_sale_hour.time_to_pickup_tuesday', time_to_pickup_tuesday)

        param.set_param('website_sale_hour.time_from_pickup_wednesday', time_from_pickup_wednesday)
        param.set_param('website_sale_hour.time_to_pickup_wednesday', time_to_pickup_wednesday)

        param.set_param('website_sale_hour.time_from_pickup_thursday', time_from_pickup_thursday)
        param.set_param('website_sale_hour.time_to_pickup_thursday', time_to_pickup_thursday)

        param.set_param('website_sale_hour.time_from_pickup_friday', time_from_pickup_friday)
        param.set_param('website_sale_hour.time_to_pickup_friday', time_to_pickup_friday)

        param.set_param('website_sale_hour.time_from_pickup_saturday', time_from_pickup_saturday)
        param.set_param('website_sale_hour.time_to_pickup_saturday', time_to_pickup_saturday)

        # Delivery Timings
        param.set_param('website_sale_hour.time_from_delivery_sunday', time_from_delivery_sunday)
        param.set_param('website_sale_hour.time_to_delivery_sunday', time_to_delivery_sunday)

        param.set_param('website_sale_hour.time_from_delivery_monday', time_from_delivery_monday)
        param.set_param('website_sale_hour.time_to_delivery_monday', time_to_delivery_monday)

        param.set_param('website_sale_hour.time_from_delivery_tuesday', time_from_delivery_tuesday)
        param.set_param('website_sale_hour.time_to_delivery_tuesday', time_to_delivery_tuesday)

        param.set_param('website_sale_hour.time_from_delivery_wednesday', time_from_delivery_wednesday)
        param.set_param('website_sale_hour.time_to_delivery_wednesday', time_to_delivery_wednesday)

        param.set_param('website_sale_hour.time_from_delivery_thursday', time_from_delivery_thursday)
        param.set_param('website_sale_hour.time_to_delivery_thursday', time_to_delivery_thursday)

        param.set_param('website_sale_hour.time_from_delivery_friday', time_from_delivery_friday)
        param.set_param('website_sale_hour.time_to_delivery_friday', time_to_delivery_friday)

        param.set_param('website_sale_hour.time_from_delivery_saturday', time_from_delivery_saturday)
        param.set_param('website_sale_hour.time_to_delivery_saturday', time_to_delivery_saturday)

        param.set_param('website_sale_hour.pre_order_kitchen_display', pre_order_kitchen_display)
        param.set_param('website_sale_hour.pos_order_kitchen_display', pos_order_kitchen_display)

    @api.constrains('time_from_pickup_sunday', 'time_to_pickup_sunday', 'time_from_pickup_monday',
                    'time_to_pickup_monday',
                    'time_from_pickup_tuesday', 'time_to_pickup_tuesday', 'time_from_pickup_wednesday',
                    'time_to_pickup_wednesday',
                    'time_from_pickup_thursday', 'time_to_pickup_thursday', 'time_from_pickup_friday',
                    'time_to_pickup_friday',
                    'time_from_pickup_saturday', 'time_to_pickup_saturday', 'sunday_from', 'sunday_to', 'monday_from',
                    'monday_to',
                    'tuesday_from', 'tuesday_to', 'wednesday_from', 'wednesday_to', 'thursday_from', 'thursday_to',
                    'friday_from',
                    'friday_to', 'saturday_from', 'saturday_to', 'future_order_from', 'future_order_to', 'pickup_time',
                    'future_order_from', 'future_order_to', 'pre_order_kitchen_display', 'delivery_time',
                    'pos_order_kitchen_display', 'time_from_delivery_sunday', 'time_to_delivery_sunday',
                    'time_from_delivery_monday', 'time_to_delivery_monday', 'time_from_delivery_tuesday',
                    'time_to_delivery_tuesday', 'time_from_delivery_wednesday', 'time_to_delivery_wednesday',
                    'time_from_delivery_thursday', 'time_to_delivery_thursday', 'time_from_delivery_friday',
                    'time_to_delivery_friday', 'time_from_delivery_saturday', 'time_to_delivery_saturday')
    def _check_time_validation(self):
        for time in self:
            if time.time_from_pickup_sunday > time.time_to_pickup_sunday or \
                    time.time_from_pickup_monday > time.time_to_pickup_monday or \
                    time.time_from_pickup_tuesday > time.time_to_pickup_tuesday or \
                    time.time_from_pickup_wednesday > time.time_to_pickup_wednesday or \
                    time.time_from_pickup_thursday > time.time_to_pickup_thursday or \
                    time.time_from_pickup_friday > time.time_to_pickup_friday or \
                    time.time_from_pickup_saturday > time.time_to_pickup_saturday or \
                    time.time_from_delivery_sunday > time.time_to_delivery_sunday or \
                    time.time_from_delivery_monday > time.time_to_delivery_monday or \
                    time.time_from_delivery_tuesday > time.time_to_delivery_tuesday or \
                    time.time_from_delivery_wednesday > time.time_to_delivery_wednesday or \
                    time.time_from_delivery_thursday > time.time_to_delivery_thursday or \
                    time.time_from_delivery_friday > time.time_to_delivery_friday or \
                    time.time_from_delivery_saturday > time.time_to_delivery_saturday or \
                    time.sunday_from > time.sunday_to or time.monday_from > time.monday_to or \
                    time.tuesday_from > time.tuesday_to or time.wednesday_from > time.wednesday_to or \
                    time.thursday_from > time.thursday_to or time.friday_from > time.friday_to or \
                    time.saturday_from > time.saturday_to or time.future_order_from > time.future_order_to:
                raise ValidationError(_("'From' time range should be less than 'To' time range."))
            if time.time_from_pickup_sunday > 24 or time.time_to_pickup_sunday > 24 or \
                    time.time_from_pickup_monday > 24 or time.time_to_pickup_monday > 24 or \
                    time.time_from_pickup_tuesday > 24 or time.time_to_pickup_tuesday > 24 or \
                    time.time_from_pickup_wednesday > 24 or time.time_to_pickup_wednesday > 24 or \
                    time.time_from_pickup_thursday > 24 or time.time_to_pickup_thursday > 24 or \
                    time.time_from_pickup_friday > 24 or time.time_to_pickup_friday > 24 or \
                    time.time_from_pickup_saturday > 24 or time.time_to_pickup_saturday > 24 or \
                    time.sunday_from > 24 or time.sunday_to > 24 or time.monday_from > 24 or \
                    time.monday_to > 24 or time.tuesday_from > 24 or time.tuesday_to > 24 or \
                    time.wednesday_from > 24 or time.wednesday_to > 24 or time.thursday_from > 24 or \
                    time.thursday_to > 24 or time.friday_from > 24 or time.friday_to > 24 or \
                    time.saturday_from > 24 or time.saturday_to > 24 or time.pickup_time > 24 or \
                    time.pre_order_kitchen_display > 24 or time.pos_order_kitchen_display > 24 or \
                    time.delivery_time > 24 or time.time_from_delivery_sunday > 24 or\
                    time.time_to_delivery_sunday > 24 or time.time_from_delivery_monday > 24 or\
                    time.time_to_delivery_monday > 24 or time.time_from_delivery_tuesday > 24 or\
                    time.time_to_delivery_tuesday > 24 or time.time_from_delivery_wednesday > 24 or\
                    time.time_to_delivery_wednesday > 24 or time.time_from_delivery_thursday > 24 or\
                    time.time_to_delivery_thursday > 24 or time.time_from_delivery_friday > 24 or\
                    time.time_to_delivery_friday > 24 or time.time_from_delivery_saturday > 24 or\
                    time.time_to_delivery_saturday > 24:
                raise ValidationError(_("Invalid time."))
            if time.future_order_from_type == 'minute' and time.future_order_from > 60 or \
                    time.future_order_from_type == 'hour' and time.future_order_from > 24 or \
                    time.future_order_to_type == 'minute' and time.future_order_to > 60 or \
                    time.future_order_to_type == 'hour' and time.future_order_to > 24:
                raise ValidationError(_("Enter a valid Future Order Time."))
