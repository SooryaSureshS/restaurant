from odoo import models, fields, api


class PaymentCardDetails(models.Model):
    _name = 'payment.card.data'
    _description = 'Payment Card Details'

    acquirer_id = fields.Many2one(
        string="Acquirer Account", comodel_name='payment.acquirer', required=True)
    provider = fields.Selection(related='acquirer_id.provider')
    name = fields.Char(
        string="Name", help="The anonymized acquirer reference of the payment method",
        required=True)
    partner_id = fields.Many2one(string="Partner", comodel_name='res.partner', required=True)
    company_id = fields.Many2one(  # Indexed to speed-up ORM searches (from ir_rule or others)
        related='acquirer_id.company_id', store=True, index=True)
    acquirer_ref = fields.Char(
        string="Acquirer Reference", help="The acquirer reference of the token of the transaction",
        required=True)  # This is not the same thing as the acquirer reference of the transaction
    transaction_ids = fields.One2many(
        string="Payment Transactions", comodel_name='payment.transaction', inverse_name='token_id')
    verified = fields.Boolean(string="Verified")
    active = fields.Boolean(string="Active", default=True)
    card_number = fields.Char(string="Card Number")
    card_cvc = fields.Char(string="CVC Number")
    card_holder_name = fields.Char(string="Card Holder Name")
    card_expiry = fields.Char(string="Card Expiry")
    card_brand = fields.Char(string="Card Brand")
    key = fields.Char()


