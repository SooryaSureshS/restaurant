
import base64

from odoo import models, fields, api
from odoo.modules import get_module_resource


class Theme(models.TransientModel):
    _name = "theme.data"

    def _get_current_theme(self):
        return self.env['theme.data.stored'].sudo().search([], limit=1).name

    name = fields.Selection([
        ('default', 'Default'),
        ('two', 'Green'),
        ('three', 'Black'),
    ], 'Theme', required=True, default=_get_current_theme)

    @api.onchange('name')
    def onchange_name(self):
        theme = self.sudo().env.ref('vista_backend_theme.theme_data_stored')
        if theme:
            theme.name = self.name
        else:
            theme.create({
                'name': self.name
            })

    def action_apply(self):
        name = self.env['theme.data.stored'].sudo().search([], limit=1).name
        if name == 'two':
            self.env.ref('vista_backend_theme.vista_theme_css_black').active = False
            self.env.ref('vista_backend_theme.vista_theme_css_login_black').active = False
            self.env.ref('vista_backend_theme.vista_theme_css_green').active = True
            self.env.ref('vista_backend_theme.vista_theme_css_login_green').active = True
            self.icon_change_theme_green()
        elif name == 'three':
            self.env.ref('vista_backend_theme.vista_theme_css_green').active = False
            self.env.ref('vista_backend_theme.vista_theme_css_login_green').active = False
            self.env.ref('vista_backend_theme.vista_theme_css_black').active = True
            self.env.ref('vista_backend_theme.vista_theme_css_login_black').active = True
            self.icon_change_theme_default()
        else:
            self.env.ref('vista_backend_theme.vista_theme_css_green').active = False
            self.env.ref('vista_backend_theme.vista_theme_css_black').active = False
            self.env.ref('vista_backend_theme.vista_theme_css_login_green').active = False
            self.env.ref('vista_backend_theme.vista_theme_css_login_black').active = False
            self.icon_change_theme_default()

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def icon_change_theme_default(self):
        menu_item = self.env['ir.ui.menu'].sudo().search([('parent_id', '=', False)])
        for menu in menu_item:
            if menu.name == 'Contacts':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img', 'icons',
                    'contacts.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Link Tracker':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img', 'icons',
                    'link-tracker.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Dashboards':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img', 'icons',
                    'dashboards.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Sales':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img', 'icons',
                    'sales.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Invoicing':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img', 'icons',
                    'accounting.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Accounting':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img', 'icons',
                    'accounting.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Inventory':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img', 'icons',
                    'inventory.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Purchase':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img', 'icons',
                    'purchase.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Calendar':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img', 'icons',
                    'calendar.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'CRM':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img', 'icons',
                    'crm.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Note':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img', 'icons',
                    'note.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Website':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img', 'icons',
                    'website.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Point of Sale':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img', 'icons',
                    'pos.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Manufacturing':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img', 'icons',
                    'manufacturing.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Repairs':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img', 'icons',
                    'repairs.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Email Marketing':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img', 'icons',
                    'email-marketing.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'SMS Marketing':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img', 'icons',
                    'sms-marketing.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Project':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img', 'icons',
                    'project.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Surveys':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img', 'icons',
                    'surveys.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Employees':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img', 'icons',
                    'employee.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Recruitment':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img', 'icons',
                    'recruitment.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Attendances':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img', 'icons',
                    'attendances.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Time Off':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img', 'icons',
                    'timeoff.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Expenses':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img', 'icons',
                    'expenses.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Maintenance':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img', 'icons',
                    'maintenance.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Live Chat':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img', 'icons',
                    'live-chat.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Lunch':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img', 'icons',
                    'lunch.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Fleet':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img', 'icons',
                    'fleet.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Timesheets':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img', 'icons',
                    'timesheets.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Events':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img', 'icons',
                    'events.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'eLearning':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img', 'icons',
                    'elearning.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Members':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img', 'icons',
                    'members.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Apps':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img', 'icons',
                    'apps.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Discuss':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img', 'icons',
                    'discuss.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Settings':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img', 'icons',
                    'settinga.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            else:
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img',
                    'icons_green',
                    'common.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})

    def icon_change_theme_green(self):
        menu_item = self.env['ir.ui.menu'].sudo().search([('parent_id', '=', False)])
        for menu in menu_item:
            if menu.name == 'Contacts':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img',
                    'icons_green',
                    'contacts.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Link Tracker':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img',
                    'icons_green',
                    'link-tracker.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Dashboards':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img',
                    'icons_green',
                    'dashboards.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Sales':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img',
                    'icons_green',
                    'sales.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Invoicing':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img',
                    'icons_green',
                    'accounting.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Inventory':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img',
                    'icons_green',
                    'inventory.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Purchase':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img',
                    'icons_green',
                    'purchase.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Calendar':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img',
                    'icons_green',
                    'calendar.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'CRM':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img',
                    'icons_green',
                    'crm.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Note':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img',
                    'icons_green',
                    'note.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Website':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img',
                    'icons_green',
                    'website.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Point of Sale':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img',
                    'icons_green',
                    'pos.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Manufacturing':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img',
                    'icons_green',
                    'manufacturing.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Repairs':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img',
                    'icons_green',
                    'repairs.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Email Marketing':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img',
                    'icons_green',
                    'email-marketing.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'SMS Marketing':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img',
                    'icons_green',
                    'sms-marketing.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Project':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img',
                    'icons_green',
                    'project.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Surveys':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img',
                    'icons_green',
                    'surveys.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Employees':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img',
                    'icons_green',
                    'employee.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Recruitment':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img',
                    'icons_green',
                    'recruitment.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Attendances':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img',
                    'icons_green',
                    'attendances.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Time Off':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img',
                    'icons_green',
                    'timeoff.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Expenses':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img',
                    'icons_green',
                    'expenses.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Maintenance':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img',
                    'icons_green',
                    'maintenance.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Live Chat':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img',
                    'icons_green',
                    'live-chat.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Lunch':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img',
                    'icons_green',
                    'lunch.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Fleet':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img',
                    'icons_green',
                    'fleet.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Timesheets':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img',
                    'icons_green',
                    'timesheets.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Events':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img',
                    'icons_green',
                    'events.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'eLearning':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img',
                    'icons_green',
                    'elearning.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Members':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img',
                    'icons_green',
                    'members.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Apps':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img',
                    'icons_green',
                    'apps.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Discuss':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img',
                    'icons_green',
                    'discuss.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Settings':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img',
                    'icons_green',
                    'settinga.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            elif menu.name == 'Accounting':
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img',
                    'icons_green',
                    'accounting.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})
            else:
                img_path = get_module_resource(
                    'vista_backend_theme', 'static', 'src', 'img',
                    'icons_green',
                    'common.png')
                menu.write({'web_icon_data': base64.b64encode(
                    open(img_path, "rb").read())})

class ThemeStored(models.Model):
    _name = "theme.data.stored"

    name = fields.Selection([
        ('default', 'Default'),
        ('two', 'Green'),
        ('three', 'Black'),
    ], 'Theme', default='default')
