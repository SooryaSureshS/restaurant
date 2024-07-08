from odoo import models, fields, api, tools, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, vals):
        if 'phone' in vals and vals['phone']:
            if 'mobile' not in vals:
                vals['mobile'] = vals['phone']
            elif not vals['mobile']:
                vals['mobile'] = vals['phone']
        record = super(ResPartner, self).create(vals)
        return record

    def write(self, vals):
        print(vals)
        if 'phone' in vals and vals['phone']:
            if 'mobile' not in vals:
                vals['mobile'] = vals['phone']
            elif not vals['mobile']:
                vals['mobile'] = vals['phone']
        record = super(ResPartner, self).write(vals)
        return record
