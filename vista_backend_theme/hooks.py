# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2021-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
import base64

from odoo import api, SUPERUSER_ID
from odoo.modules import get_module_resource


def test_pre_init_hook(cr):
    """pre init hook"""

    env = api.Environment(cr, SUPERUSER_ID, {})
    menu_item = env['ir.ui.menu'].search([('parent_id', '=', False)])

    for menu in menu_item:
        if menu.name == 'Contacts':
            img_path = get_module_resource(
                'vista_backend_theme', 'static', 'src', 'img', 'icons', 'contacts.png')
            menu.write({'web_icon_data': base64.b64encode(open(img_path, "rb").read())})
        elif menu.name == 'Link Tracker':
            img_path = get_module_resource(
                'vista_backend_theme', 'static', 'src', 'img', 'icons', 'link-tracker.png')
            menu.write({'web_icon_data': base64.b64encode(open(img_path, "rb").read())})
        elif menu.name == 'Dashboards':
            img_path = get_module_resource(
                'vista_backend_theme', 'static', 'src', 'img', 'icons', 'dashboards.png')
            menu.write({'web_icon_data': base64.b64encode(open(img_path, "rb").read())})
        elif menu.name == 'Sales':
            img_path = get_module_resource(
                'vista_backend_theme', 'static', 'src', 'img', 'icons', 'sales.png')
            menu.write({'web_icon_data': base64.b64encode(open(img_path, "rb").read())})
        elif menu.name == 'Invoicing':
            img_path = get_module_resource(
                'vista_backend_theme', 'static', 'src', 'img', 'icons', 'accounting.png')
            menu.write({'web_icon_data': base64.b64encode(open(img_path, "rb").read())})
        elif menu.name == 'Inventory':
            img_path = get_module_resource(
                'vista_backend_theme', 'static', 'src', 'img', 'icons', 'inventory.png')
            menu.write({'web_icon_data': base64.b64encode(open(img_path, "rb").read())})
        elif menu.name == 'Purchase':
            img_path = get_module_resource(
                'vista_backend_theme', 'static', 'src', 'img', 'icons', 'purchase.png')
            menu.write({'web_icon_data': base64.b64encode(open(img_path, "rb").read())})
        elif menu.name == 'Calendar':
            img_path = get_module_resource(
                'vista_backend_theme', 'static', 'src', 'img', 'icons', 'calendar.png')
            menu.write({'web_icon_data': base64.b64encode(open(img_path, "rb").read())})
        elif menu.name == 'CRM':
            img_path = get_module_resource(
                'vista_backend_theme', 'static', 'src', 'img', 'icons', 'crm.png')
            menu.write({'web_icon_data': base64.b64encode(open(img_path, "rb").read())})
        elif menu.name == 'Note':
            img_path = get_module_resource(
                'vista_backend_theme', 'static', 'src', 'img', 'icons', 'note.png')
            menu.write({'web_icon_data': base64.b64encode(open(img_path, "rb").read())})
        elif menu.name == 'Website':
            img_path = get_module_resource(
                'vista_backend_theme', 'static', 'src', 'img', 'icons', 'website.png')
            menu.write({'web_icon_data': base64.b64encode(open(img_path, "rb").read())})
        elif menu.name == 'Point of Sale':
            img_path = get_module_resource(
                'vista_backend_theme', 'static', 'src', 'img', 'icons', 'pos.png')
            menu.write({'web_icon_data': base64.b64encode(open(img_path, "rb").read())})
        elif menu.name == 'Manufacturing':
            img_path = get_module_resource(
                'vista_backend_theme', 'static', 'src', 'img', 'icons', 'manufacturing.png')
            menu.write({'web_icon_data': base64.b64encode(open(img_path, "rb").read())})
        elif menu.name == 'Repairs':
            img_path = get_module_resource(
                'vista_backend_theme', 'static', 'src', 'img', 'icons', 'repairs.png')
            menu.write({'web_icon_data': base64.b64encode(open(img_path, "rb").read())})
        elif menu.name == 'Email Marketing':
            img_path = get_module_resource(
                'vista_backend_theme', 'static', 'src', 'img', 'icons', 'email-marketing.png')
            menu.write({'web_icon_data': base64.b64encode(open(img_path, "rb").read())})
        elif menu.name == 'SMS Marketing':
            img_path = get_module_resource(
                'vista_backend_theme', 'static', 'src', 'img', 'icons', 'sms-marketing.png')
            menu.write({'web_icon_data': base64.b64encode(open(img_path, "rb").read())})
        elif menu.name == 'Project':
            img_path = get_module_resource(
                'vista_backend_theme', 'static', 'src', 'img', 'icons', 'project.png')
            menu.write({'web_icon_data': base64.b64encode(open(img_path, "rb").read())})
        elif menu.name == 'Surveys':
            img_path = get_module_resource(
                'vista_backend_theme', 'static', 'src', 'img', 'icons', 'surveys.png')
            menu.write({'web_icon_data': base64.b64encode(open(img_path, "rb").read())})
        elif menu.name == 'Employees':
            img_path = get_module_resource(
                'vista_backend_theme', 'static', 'src', 'img', 'icons', 'employee.png')
            menu.write({'web_icon_data': base64.b64encode(open(img_path, "rb").read())})
        elif menu.name == 'Recruitment':
            img_path = get_module_resource(
                'vista_backend_theme', 'static', 'src', 'img', 'icons', 'recruitment.png')
            menu.write({'web_icon_data': base64.b64encode(open(img_path, "rb").read())})
        elif menu.name == 'Attendances':
            img_path = get_module_resource(
                'vista_backend_theme', 'static', 'src', 'img', 'icons', 'attendances.png')
            menu.write({'web_icon_data': base64.b64encode(open(img_path, "rb").read())})
        elif menu.name == 'Time Off':
            img_path = get_module_resource(
                'vista_backend_theme', 'static', 'src', 'img', 'icons', 'timeoff.png')
            menu.write({'web_icon_data': base64.b64encode(open(img_path, "rb").read())})
        elif menu.name == 'Expenses':
            img_path = get_module_resource(
                'vista_backend_theme', 'static', 'src', 'img', 'icons', 'expenses.png')
            menu.write({'web_icon_data': base64.b64encode(open(img_path, "rb").read())})
        elif menu.name == 'Maintenance':
            img_path = get_module_resource(
                'vista_backend_theme', 'static', 'src', 'img', 'icons', 'maintenance.png')
            menu.write({'web_icon_data': base64.b64encode(open(img_path, "rb").read())})
        elif menu.name == 'Live Chat':
            img_path = get_module_resource(
                'vista_backend_theme', 'static', 'src', 'img', 'icons', 'live-chat.png')
            menu.write({'web_icon_data': base64.b64encode(open(img_path, "rb").read())})
        elif menu.name == 'Lunch':
            img_path = get_module_resource(
                'vista_backend_theme', 'static', 'src', 'img', 'icons', 'lunch.png')
            menu.write({'web_icon_data': base64.b64encode(open(img_path, "rb").read())})
        elif menu.name == 'Fleet':
            img_path = get_module_resource(
                'vista_backend_theme', 'static', 'src', 'img', 'icons', 'fleet.png')
            menu.write({'web_icon_data': base64.b64encode(open(img_path, "rb").read())})
        elif menu.name == 'Timesheets':
            img_path = get_module_resource(
                'vista_backend_theme', 'static', 'src', 'img', 'icons', 'timesheets.png')
            menu.write({'web_icon_data': base64.b64encode(open(img_path, "rb").read())})
        elif menu.name == 'Events':
            img_path = get_module_resource(
                'vista_backend_theme', 'static', 'src', 'img', 'icons', 'events.png')
            menu.write({'web_icon_data': base64.b64encode(open(img_path, "rb").read())})
        elif menu.name == 'eLearning':
            img_path = get_module_resource(
                'vista_backend_theme', 'static', 'src', 'img', 'icons', 'elearning.png')
            menu.write({'web_icon_data': base64.b64encode(open(img_path, "rb").read())})
        elif menu.name == 'Members':
            img_path = get_module_resource(
                'vista_backend_theme', 'static', 'src', 'img', 'icons', 'members.png')
            menu.write({'web_icon_data': base64.b64encode(open(img_path, "rb").read())})
        else:
            img_path = get_module_resource(
                'vista_backend_theme', 'static', 'src', 'img', 'icons', 'common.png')
            menu.write({'web_icon_data': base64.b64encode(open(img_path, "rb").read())})


def test_post_init_hook(cr, registry):
    """post init hook"""

    env = api.Environment(cr, SUPERUSER_ID, {})
