from odoo import models


class ResGroups(models.Model):
    _inherit = 'res.groups'

    def write(self, vals):
        res = super(ResGroups, self).write(vals)
        menu_list = []
        menus = self.env['ir.ui.menu'].sudo().search([])
        check_list1 = ['Scheduling', 'Scheduling/Published Scheduling', 'Discuss', 'Employees', 'Employees/Notice Board']
        for i in menus:
            if i.parent_id and (i.parent_id.name == 'Discuss'):
                check_list1.append(i.complete_name)
        for i in menus:
            if i.complete_name not in check_list1:
                menu_list.append(i)
        for rec in self:
            if rec.name == "Employee" and rec.users:
                for menu in menu_list:
                    menu.write({'restrict_user_ids': [(6, 0, rec.users.ids)]})
        return res
