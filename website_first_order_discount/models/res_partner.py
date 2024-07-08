from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'
    first_order_discount = fields.Boolean(string="First Order discount")
    

class ResUsers(models.Model):
    _inherit = 'res.users'

    #website new user first order discount
    @api.model
    def create(self, vals_list):
        res = super(ResUsers, self).create(vals_list)
        if res:
            group_users = self.env.ref('base.group_portal').mapped('users.id')
            if res.id in group_users:
                res.partner_id.first_order_discount = True
        return res


    
    
    
