from odoo import models, fields, api, _
from datetime import datetime
import datetime


class PosConfigParams(models.Model):
    _inherit = 'pos.config'

    enable_gift_card = fields.Boolean('Enable Gift Card')
    gift_card_product_id = fields.Many2one('product.product', string="Gift Card Product")
    enable_journal_id = fields.Many2one("pos.payment.method", string="Enable Journal")
    manual_card_number = fields.Boolean('Manual Card No.')
    default_exp_date = fields.Integer('Default Card Expire Months')
    msg_before_card_pay = fields.Boolean('Confirm Message Before Card Payment')
    print_gift_card = fields.Boolean('Print Gift Card')


class PosOrder(models.Model):
    _inherit = 'pos.order'

    redeem_card_amount = fields.Float("Gift Card Redeem Amount")

    @api.model
    def create_from_ui(self, orders, draft=False):
        # Keep only new orders
        res = super(PosOrder, self).create_from_ui(orders, draft=False)
        pos_orders = self.browse([each.get('id') for each in res])
        existing_orders = pos_orders.read(['pos_reference'])
        existing_references = set([o['pos_reference'] for o in existing_orders])
        orders_to_read = [o for o in orders if o['data']['name'] in existing_references]

        for tmp_order in orders_to_read:
            order = tmp_order['data']
            order_obj = self.search([('pos_reference', '=', order['name'])])
            if order.get('giftcard'):
                for create_details in order.get('giftcard'):
                    vals = {
                        'card_no': create_details.get('giftcard_card_no'),
                        'card_value': create_details.get('giftcard_amount'),
                        'customer_id': create_details.get('giftcard_customer') or False,
                        'expire_date': create_details.get('giftcard_expire_date'),
                        'card_type': create_details.get('card_type'),
                    }
                    self.env['pos.gift.card'].create(vals)

            print("asdfghjkl", order)
            #  create redeem giftcard for use
            if order.get('redeem') and order_obj:
                for redeem_details in order.get('redeem'):
                    redeem_vals = {
                        'pos_order_id': order_obj.id,
                        'order_date': order_obj.date_order,
                        'customer_id': redeem_details.get('card_customer_id') or False,
                        'card_id': redeem_details.get('redeem_card_no'),
                        'amount': redeem_details.get('redeem_card_amount'),
                    }
                    order_obj.write({'redeem_card_amount': redeem_details.get('redeem_card_amount')})
                    use_giftcard = self.env['pos.gift.card.use'].create(redeem_vals)
                    if use_giftcard and use_giftcard.card_id:
                        use_giftcard.card_id.write(
                            {'card_value': use_giftcard.card_id.card_value - use_giftcard.amount})
        return res


class PosPaymentMethods(models.Model):
    _inherit = 'pos.payment.method'

    allow_for_gift_cards = fields.Boolean(string="Allow For Gift Card")
