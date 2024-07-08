# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval


# Loyalty program details
class POSLoyaltyProgram(models.Model):
    _name = 'pos.loyalty.program'
    _description = 'Loyalty Program'

    name = fields.Char(string='Loyalty Program Name', index=True, required=True)
    points = fields.Float(string='Point per $ spent', help="How many loyalty points are given to the customer")
    rule_ids = fields.One2many('loyalty.rule', 'loyalty_program_id', string='Rules')
    reward_ids = fields.One2many('loyalty.reward', 'loyalty_program_id', string='Rewards')
    active = fields.Boolean(default=True)


# Loyalty rules
class LoyaltyRule(models.Model):
    _name = 'loyalty.rule'
    _description = 'Loyalty Rule'

    name = fields.Char(index=True, required=True, help="An internal identification for this loyalty program rule")
    loyalty_program_id = fields.Many2one('pos.loyalty.program', string='Loyalty Program')
    points_quantity = fields.Float(string="Points per Unit")
    points_currency = fields.Float(string="Points per $ spent")
    rule_domain = fields.Char()
    valid_product_ids = fields.One2many('product.product', compute='_compute_valid_product_ids')

    @api.depends('rule_domain')
    def _compute_valid_product_ids(self):
        for rule in self:
            if rule.rule_domain:
                domain = safe_eval(rule.rule_domain)
                domain = expression.AND([domain, [('available_in_pos', '=', True)]])
                rule.valid_product_ids = self.env['product.product'].search(domain)
            else:
                rule.valid_product_ids = self.env['product.product'].search([('available_in_pos', '=', True)])


# Loyalty rewards module
class LoyaltyReward(models.Model):
    _name = 'loyalty.reward'
    _description = 'Loyalty Reward'

    name = fields.Char(index=True, required=True, help='An internal identification for this loyalty reward')
    loyalty_program_id = fields.Many2one('pos.loyalty.program', string='Loyalty Program', help='The Loyalty Program this reward belongs to')
    minimum_points = fields.Float(help='The minimum amount of points the customer must have to qualify for this reward')
    reward_type = fields.Selection([('gift', 'Free Product'), ('discount', 'Discount')], required=True, help='The type of the reward', default="gift")
    gift_product_id = fields.Many2one('product.product', string='Gift Product', help='The product given as a reward')
    point_cost = fields.Float(string='Reward Cost')
    discount_product_id = fields.Many2one('product.product', string='Discount Product', help='Discount Product')
    discount_type = fields.Selection([
        ('percentage', 'Percentage'),
        ('fixed_amount', 'Fixed Amount')], default="percentage",
        help="Percentage - Entered percentage discount will be provided\n" +
             "Amount - Entered fixed amount discount will be provided")
    discount_percentage = fields.Float(string="Discount", default=10,
                                       help='The discount in percentage, between 1 and 100')
    discount_apply_on = fields.Selection([
        ('on_order', 'On Order'),
        ('cheapest_product', 'On Cheapest Product'),
        ('specific_products', 'On Specific Products')], default="on_order",
        help="On Order - Discount on whole order\n" +
             "Cheapest product - Discount on cheapest product of the order\n" +
             "Specific products - Discount on selected specific products")
    discount_specific_product_ids = fields.Many2many('product.product', string="Products",
                                                     help="Products that will be discounted if the discount is applied on specific products")
    discount_max_amount = fields.Float(default=0,
                                       help="Maximum amount of discount that can be provided")
    discount_fixed_amount = fields.Float(string="Fixed Amount", help='The discount in fixed amount')
    minimum_amount = fields.Float(string="Minimum Order Amount")

    @api.constrains('reward_type', 'gift_product_id')
    def _check_gift_product(self):
        if self.filtered(lambda reward: reward.reward_type == 'gift' and not reward.gift_product_id):
            raise ValidationError(_('The gift product field is mandatory for gift rewards'))

    @api.constrains('reward_type', 'discount_product_id')
    def _check_discount_product(self):
        if self.filtered(lambda reward: reward.reward_type == 'discount' and not reward.discount_product_id):
            raise ValidationError(_('The discount product field is mandatory for discount rewards'))


# Loyalty points field for customers
class ResPartner(models.Model):
    _inherit = 'res.partner'

    loyalty_points = fields.Float(company_dependent=True, help='The loyalty points the user won as part of a Loyalty Program')


# Loyalty points won or lost in an order
class PosOrder(models.Model):
    _inherit = 'pos.order'

    loyalty_points = fields.Float(help='The amount of Loyalty points the customer won or lost with this order')

    # Update loyalty points to the pos order
    @api.model
    def _order_fields(self, ui_order):
        fields = super(PosOrder, self)._order_fields(ui_order)
        fields['loyalty_points'] = ui_order.get('loyalty_points', 0)
        return fields

    @api.model
    def create_from_ui(self, orders, draft=False):
        order_ids = super(PosOrder, self).create_from_ui(orders, draft)
        for order in self.sudo().browse([o['id'] for o in order_ids]):
            if order.loyalty_points != 0 and order.partner_id:
                order.partner_id.loyalty_points += order.loyalty_points
        return order_ids


# Loyalty rule configuration
class PosConfig(models.Model):
    _inherit = 'pos.config'

    def _default_loyalty_program(self):
        return self.env['pos.loyalty.program'].search([], limit=1)

    module_pos_loyalty = fields.Boolean(default=True)
    loyalty_id = fields.Many2one('pos.loyalty.program', string='Pos Loyalty Program', help='The loyalty program used by this point of sale.', default=_default_loyalty_program)

    # Enabling loyalty program
    @api.onchange('module_pos_loyalty')
    def _onchange_module_pos_loyalty(self):
        if self.module_pos_loyalty:
            self.loyalty_id = self._default_loyalty_program()
        else:
            self.loyalty_id = False

    @api.model
    def set_loyalty_program_to_main_config(self):
        main_config = self.env.ref('point_of_sale.pos_config_main')
        default_loyalty_program = self._default_loyalty_program()
        main_config.write({'module_pos_loyalty': bool(default_loyalty_program), 'loyalty_id': default_loyalty_program.id})


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def write(self, vals):
        if 'active' in vals and not vals['active']:
            product_in_reward = self.env['loyalty.reward'].sudo().search(['|', ('gift_product_id', 'in', self.ids),
                                                                 ('discount_product_id', 'in', self.ids)], limit=1)
            if product_in_reward:
                raise ValidationError(_("Cannot archive because it's used in a point of sales loyalty program."))
        super().write(vals)
