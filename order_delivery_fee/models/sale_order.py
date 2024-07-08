from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def create(self, vals_list):
        res = super(SaleOrder, self).create(vals_list)
        if res.order_id.website_delivery_type:
            if res.order_id.website_delivery_type == 'delivery':
                product = res.order_id.carrier_id.product_id
                if product:
                    if res.product_id.id == product.id:
                        if res.order_id.partner_id.is_merchant:
                                minimum_amount = self.env['ir.config_parameter'].sudo().get_param('order_delivery_fee.minimum_amount') or 15
                                amount = 0
                                percentage_formula = float((res.order_id.amount_total*26)/100)
                                if minimum_amount:
                                    minimum_amount=float(minimum_amount)
                                if percentage_formula>minimum_amount:
                                    amount = percentage_formula
                                else:
                                    amount = minimum_amount
                                res.price_unit = amount
                        else:
                            minimum_amount = self.env['ir.config_parameter'].sudo().get_param('order_delivery_fee.minimum_amount') or 15
                            res.price_unit = minimum_amount

        return res


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    minimum_amount = fields.Integer(string='Minimum Amount',
                             config_parameter="order_delivery_fee.minimum_amount")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

        res['minimum_amount'] = int(
            self.env['ir.config_parameter'].sudo().get_param('order_delivery_fee.minimum_amount', default=0))
        return res

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('order_delivery_fee.minimum_amount', self.minimum_amount)

        super(ResConfigSettings, self).set_values()

class ResPartner(models.Model):
    _inherit = 'res.partner'
    is_merchant = fields.Boolean('Is Merchant')

