from odoo import models, fields, api, _
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

class ContactUs(models.Model):
    _inherit = 'website'


    def get_restaurant_demo(self):

        res_config_settings = self.env['ir.config_parameter'].sudo()

        #opening hours
        monday_opening_hours = res_config_settings.get_param('website_sale_hour.monday_from')
        monday = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(monday_opening_hours) * 60, 60))
        time = datetime.strptime(monday, "%H:%M")
        time=time.strftime('%H:%M')
        time = datetime.strptime(time, "%H:%M")
        monday_opening_time=time.strftime("%I:%M %p")
        tuesday_opening_hours = res_config_settings.get_param('website_sale_hour.tuesday_from')
        tuesday = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(tuesday_opening_hours) * 60, 60))
        time = datetime.strptime(tuesday, "%H:%M")
        time = time.strftime('%H:%M')
        time = datetime.strptime(time, "%H:%M")
        tuesday_opening_time = time.strftime("%I:%M %p")
        wednesday_opening_hours = res_config_settings.get_param('website_sale_hour.wednesday_from')
        wednesday = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(wednesday_opening_hours) * 60, 60))
        time = datetime.strptime(wednesday, "%H:%M")
        time = time.strftime('%H:%M')
        time = datetime.strptime(time, "%H:%M")
        wednesday_opening_time = time.strftime("%I:%M %p")
        thursday_opening_hours = res_config_settings.get_param('website_sale_hour.thursday_from')
        thursday = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(thursday_opening_hours) * 60, 60))
        time = datetime.strptime(thursday, "%H:%M")
        time = time.strftime('%H:%M')
        time = datetime.strptime(time, "%H:%M")
        thursday_opening_time = time.strftime("%I:%M %p")
        friday_opening_hours = res_config_settings.get_param('website_sale_hour.friday_from')
        friday = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(friday_opening_hours) * 60, 60))
        time = datetime.strptime(friday, "%H:%M")
        time = time.strftime('%H:%M')
        time = datetime.strptime(time, "%H:%M")
        friday_opening_time = time.strftime("%I:%M %p")
        saturday_opening_hours = res_config_settings.get_param('website_sale_hour.saturday_from')
        saturday = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(saturday_opening_hours) * 60, 60))
        time = datetime.strptime(saturday, "%H:%M")
        time = time.strftime('%H:%M')
        time = datetime.strptime(time, "%H:%M")
        saturday_opening_time = time.strftime("%I:%M %p")
        sunday_opening_hours = res_config_settings.get_param('website_sale_hour.sunday_from')
        sunday = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(sunday_opening_hours) * 60, 60))
        time = datetime.strptime(sunday, "%H:%M")
        time = time.strftime('%H:%M')
        time = datetime.strptime(time, "%H:%M")
        sunday_opening_time = time.strftime("%I:%M %p")

        #closing hours
        monday_closing_hours = res_config_settings.get_param('website_sale_hour.monday_to')
        monday = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(monday_closing_hours) * 60, 60))
        time = datetime.strptime(monday, "%H:%M")
        time = time.strftime('%H:%M')
        time = datetime.strptime(time, "%H:%M")
        monday_closing_time = time.strftime("%I:%M %p")
        tuesday_closing_hours = res_config_settings.get_param('website_sale_hour.tuesday_to')
        tuesday = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(tuesday_closing_hours) * 60, 60))
        time = datetime.strptime(tuesday, "%H:%M")
        time = time.strftime('%H:%M')
        time = datetime.strptime(time, "%H:%M")
        tuesday_closing_time = time.strftime("%I:%M %p")
        wednesday_closing_hours = res_config_settings.get_param('website_sale_hour.wednesday_to')
        wednesday = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(wednesday_closing_hours) * 60, 60))
        time = datetime.strptime(wednesday, "%H:%M")
        time = time.strftime('%H:%M')
        time = datetime.strptime(time, "%H:%M")
        wednesday_closing_time = time.strftime("%I:%M %p")
        thursday_closing_hours = res_config_settings.get_param('website_sale_hour.thursday_to')
        thursday = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(thursday_closing_hours) * 60, 60))
        time = datetime.strptime(thursday, "%H:%M")
        time = time.strftime('%H:%M')
        time = datetime.strptime(time, "%H:%M")
        thursday_closing_time = time.strftime("%I:%M %p")
        friday_closing_hours = res_config_settings.get_param('website_sale_hour.friday_to')
        friday = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(friday_closing_hours) * 60, 60))
        time = datetime.strptime(friday, "%H:%M")
        time = time.strftime('%H:%M')
        time = datetime.strptime(time, "%H:%M")
        friday_closing_time = time.strftime("%I:%M %p")
        saturday_closing_hours = res_config_settings.get_param('website_sale_hour.saturday_to')
        saturday = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(saturday_closing_hours) * 60, 60))
        time = datetime.strptime(saturday, "%H:%M")
        time = time.strftime('%H:%M')
        time = datetime.strptime(time, "%H:%M")
        saturday_closing_time = time.strftime("%I:%M %p")
        sunday_closing_hours = res_config_settings.get_param('website_sale_hour.sunday_to')
        sunday = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(sunday_closing_hours) * 60, 60))
        time = datetime.strptime(sunday, "%H:%M")
        time = time.strftime('%H:%M')
        time = datetime.strptime(time, "%H:%M")
        sunday_closing_time = time.strftime("%I:%M %p")

        details = {'monday_opening_time': monday_opening_time,'tuesday_opening_time':tuesday_opening_time,'wednesday_opening_time':wednesday_opening_time ,
                   'thursday_opening_time':thursday_opening_time,'friday_opening_time':friday_opening_time,'saturday_opening_time':saturday_opening_time,
                   'sunday_opening_time':sunday_opening_time,'monday_closing_time':monday_closing_time,'tuesday_closing_time':tuesday_closing_time,
                   'wednesday_closing_time':wednesday_closing_time,'thursday_closing_time':thursday_closing_time,'friday_closing_time':friday_closing_time,
                   'saturday_closing_time':saturday_closing_time,'sunday_closing_time':sunday_closing_time

                         }

        return details

