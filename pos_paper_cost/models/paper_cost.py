from odoo import fields,models,api,_


class PaperCost(models.Model):
    _name = 'paper.cost'
    _rec_name = "session_id"
    _description = "Papper Cost"

    session_id = fields.Many2one('pos.session')
    pos_order_ids = fields.Many2many('pos.order')
    product_id = fields.Many2one('product.product',string="Product")
    qty = fields.Integer("Quantity")
    cost_price = fields.Float('Cost Price',compute="compute_cost_price")

    @api.depends('qty')
    def compute_cost_price(self):
        for cost in self:
            if cost.qty > 0:
                cost.cost_price = cost.qty * cost.product_id.standard_price
            else:
                cost.cost_price = 0.0