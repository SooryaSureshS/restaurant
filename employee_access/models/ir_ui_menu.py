from odoo import models, api


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    def create(self, vals):
        res = super(IrUiMenu, self).create(vals)
        try:
            group = self.env['ir.ui.menu'].sudo().search([('name', '=', 'Employee')], limit=1)
            if group:
                if group.users:
                    for rec in self:
                        if rec.complete_name not in ['Scheduling', 'Scheduling/Published Scheduling', 'Discuss']:
                            rec.write({'restrict_user_ids': [(6, 0, group.users.ids)]})
        except:
            pass
        return res
