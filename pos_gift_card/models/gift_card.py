import logging
from odoo import models, fields, api, _
import time, datetime

_logger = logging.getLogger(__name__)


class pos_gift_card(models.Model):
    _name = 'pos.gift.card'
    _rec_name = 'card_no'
    _description = 'Gift Cards'
    _order = 'id desc'

    def random_cardno(self):
        return int(time.time())

    card_no = fields.Char(string="Card No", default=random_cardno, readonly=True)
    card_value = fields.Float(string="Card Value")
    card_type = fields.Many2one('pos.gift.card.type', string="Card Type")
    customer_id = fields.Many2one('res.partner', string="Customer")
    issue_date = fields.Date(string="Issue Date", default=fields.Date.today())
    expire_date = fields.Date(string="Expire Date")
    is_active = fields.Boolean('Active', default=True)
    used_line = fields.One2many('pos.gift.card.use', 'card_id', string="Used Line")
    recharge_line = fields.One2many('pos.gift.card.recharge', 'card_id', string="Recharge Line")


class pos_gift_card_use(models.Model):
    _name = 'pos.gift.card.use'
    _rec_name = 'pos_order_id'
    _description = 'Gift card use'
    _order = 'id desc'

    card_id = fields.Many2one('pos.gift.card', string="Card", readonly=True)
    customer_id = fields.Many2one('res.partner', string="Customer")
    pos_order_id = fields.Many2one("pos.order", string="Order")
    order_date = fields.Date(string="Order Date")
    amount = fields.Float(string="Amount")


class pos_gift_card_recharge(models.Model):
    _name = 'pos.gift.card.recharge'
    _rec_name = 'amount'
    _description = 'Recharge Gift card'
    _order = 'id desc'

    card_id = fields.Many2one('pos.gift.card', string="Card", readonly=True)
    customer_id = fields.Many2one('res.partner', string="Customer")
    recharge_date = fields.Date(string="Recharge Date")
    user_id = fields.Many2one('res.users', string="User")
    amount = fields.Float(string="amount")


class pos_gift_card_type(models.Model):
    _name = 'pos.gift.card.type'
    _rec_name = 'name'
    _description = 'Types of gift card'

    name = fields.Char(string="Name")
    code = fields.Char(string=" Code")


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.depends('used_ids', 'recharged_ids')
    def compute_amount(self):
        total_amount = 0
        for ids in self:
            for card_id in ids.card_ids:
                total_amount += card_id.card_value
            ids.remaining_amount = total_amount

    card_ids = fields.One2many('pos.gift.card', 'customer_id', string="List of card")
    used_ids = fields.One2many('pos.gift.card.use', 'customer_id', string="List of used card")
    recharged_ids = fields.One2many('pos.gift.card.recharge', 'customer_id', string="List of recharged card")
    remaining_amount = fields.Char(compute=compute_amount, string="Remaining Amount", readonly=True)

