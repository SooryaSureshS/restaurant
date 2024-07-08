from odoo import models, fields, api
#
#
# class SaleTimeAndDay(models.Model):
#     _name = 'sale.day'
#
#     day_name = fields.Char()
#     day = fields.Selection([('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'),
#                             ('3', 'Thursday'), ('4', 'Friday'), ('5', 'Saturday'), ('6', 'Sunday')])
#     time_from = fields.Float('From')
#     time_to = fields.Float('to')
#
class SaleOrderTips(models.Model):
    _inherit = 'sale.order.line'

    tip_data = fields.Char()

class ProductProductTips(models.Model):
    _inherit = 'product.product'

    is_tip = fields.Boolean()

class SaleConfigTips(models.TransientModel):
    _inherit = 'res.config.settings'
    #
    # weekday_from_1 = fields.Selection([('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'),
    #                                  ('3', 'Thursday'), ('4', 'Friday'), ('5', 'Saturday'), ('6', 'Sunday')], 'From')
    # weekday_to_1 = fields.Selection([('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'),
    #                                ('3', 'Thursday'), ('4', 'Friday'), ('5', 'Saturday'), ('6', 'Sunday')], 'To')
    # time_from_1 = fields.Float('From')
    # time_to_1 = fields.Float('to')



    website_tipproduct = fields.Boolean(string="Product tips")
    website_tip_product_id = fields.Many2one('product.product', string='Tip Product',
                                     help="This product is used as reference on customer receipts.", domain="[('is_tip', '=', True)]")

    def get_values(self):
        res = super(SaleConfigTips, self).get_values()
        res.update(
            website_tipproduct=self.env['ir.config_parameter'].sudo().get_param(
                'website_tips.website_tipproduct'),
        )
        res.update(
            website_tip_product_id=int(self.env['ir.config_parameter'].sudo().get_param(
                'website_tips.website_tip_product_id')),
        )
        # a = self.env['ir.config_parameter'].sudo().get_param('website_tips.website_tip_product_id');
        # print("jjjj",a)
        # res['website_tip_product_id'] = 568
        return res

    def set_values(self):
        super(SaleConfigTips, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        website_tipproduct = self.website_tipproduct
        website_tip_product_id = self.website_tip_product_id.id
        param.set_param('website_tips.website_tipproduct', website_tipproduct)
        param.set_param('website_tips.website_tip_product_id', website_tip_product_id)
