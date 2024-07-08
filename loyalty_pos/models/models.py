# -*- coding: utf-8 -*-

from odoo import models, fields, api


class LoyaltyPos(models.Model):
    _inherit = 'pos.config'

    wk_loyalty_program_id = fields.Many2one('website.loyalty.management',string='Default Program')
    pos_loyalty = fields.Boolean()

    @api.model
    def loyalty_points(self,partner_id,loyalty_id,points_used):
        partner = self.env['res.partner'].browse([partner_id])
        loyalty_obj = self.env['website.loyalty.management'].browse([loyalty_id])
        all_rule_loyalty = []
        rule = self.env['reward.redeem.rule'].sudo().search([])

        if partner:
            values={}
            if partner.wk_website_loyalty_points-points_used < 1:
                for i in rule:
                    if i.product_ids:
                        all_rule_loyalty.append({'product_name': i.product_ids.mapped('name'), 'points_end': i.point_start})

                return {'result': 0, 'rule': all_rule_loyalty,'current_point':partner.wk_website_loyalty_points-points_used}
            elif not loyalty_obj.redeem_rule_list:
                values['no_redeem_rule'] = True
            else:
                rule = loyalty_obj.redeem_rule_list
                all_rule = []
                for i in rule:
                    if partner.wk_website_loyalty_points-points_used >= i.point_start:
                        product = []
                        for k in i.product_ids:
                            if k.available_in_pos:
                                product.append({'product_id': k.id, 'product_name': k.name})
                        if len(product)>0:
                            all_rule.append(
                                {'products': product,
                                 'line_id': i.id, 'points_end': i.point_start})
                if len(all_rule) < 1:
                    for i in rule:
                        if i.product_ids:
                            all_rule_loyalty.append(
                                {'product_name': i.product_ids.mapped('name'), 'points_end': i.point_start})

                    return {'result':'no_point','rule':all_rule_loyalty,'current_point':partner.wk_website_loyalty_points-points_used}
                else:
                    values['all_rule'] = all_rule
                    values['point']=round(partner.wk_website_loyalty_points-points_used)
            return values
        else:
            return  0

class PosOrder(models.Model):
    _inherit = 'pos.order'


    @api.model
    def get_client_sync(self):
            all_partner = self.env['res.partner'].sudo().search([])
            return [{'id':i.id,'wk_website_loyalty_points':i.wk_website_loyalty_points} for i in all_partner]

    loyalty_points = fields.Float()
    reward_redeem = fields.Boolean()
    reward_redeem_amount = fields.Float()

    wk_loyalty_program_id = fields.Many2one(
        string='Loyalty Program',
        comodel_name='website.loyalty.management'
    )


    @api.model
    def _order_fields(self, ui_order):
        fields = super(PosOrder, self)._order_fields(ui_order)
        fields['loyalty_points'] = ui_order.get('loyalty_points', 0)
        fields['reward_redeem'] = ui_order.get('reward_redeem', False)
        fields['reward_redeem_amount'] = ui_order.get('reward_redeem_amount', 0)
        fields['wk_loyalty_program_id'] = ui_order.get('wk_loyalty_program_id', False)
        return fields

    @api.model
    def create(self, orders):
        order = super(PosOrder, self).create(orders)
        if order.loyalty_points != 0 and order.partner_id:
            History = self.env['website.loyalty.history']
            domain = [
                ('pos_order_ref', '=', order.id),
                ('loyalty_process', '=', 'addition')
            ]
            already_deducted = History.search_count(domain)
            if not already_deducted:
                partner = self.env['res.partner'].sudo().search([('id', '=', order.partner_id.id)])

                vals = {
                    'partner_id': partner.id,
                    'loyalty_id': order.wk_loyalty_program_id.id,
                    'points_processed': order.loyalty_points,
                    'pos_order_ref': order.id,
                    'loyalty_process': 'addition',
                    'process_reference': 'Pos Order',
                }
                history_obj = History.create(vals)
        if order.partner_id and order.reward_redeem:
            History = self.env['website.loyalty.history']
            domain = [
                ('pos_order_ref', '=', order.id),
                ('loyalty_process', '=', 'deduction')
            ]
            already_deducted = History.search_count(domain)
            if not already_deducted:
                vals = {
                    'loyalty_id': order.wk_loyalty_program_id.id,
                    'partner_id': order.partner_id.id,
                    'points_processed': abs(order.reward_redeem_amount),
                    'pos_order_ref': order.id,
                    'redeem_amount': order.reward_redeem_amount,
                    'loyalty_process': 'deduction',
                    'process_reference': 'Pos Order',
                }
                History.create(vals)
        return order

    # @api.model
    # def create_from_ui(self, orders, draft=False):
    #     order_ids = super(PosOrder, self).create_from_ui(orders, draft)
    #     print("orderrrrrrrrrrrrrrrrrrrrrrrrrr")
    #     for order in self.sudo().browse([o['id'] for o in order_ids]):
    #         if order.loyalty_points != 0 and order.partner_id:
    #             History = self.env['website.loyalty.history']
    #             domain = [
    #                 ('pos_order_ref', '=', order.id),
    #                 ('loyalty_process', '=', 'addition')
    #             ]
    #             already_deducted = History.search_count(domain)
    #             if not already_deducted:
    #
    #                 partner = self.env['res.partner'].sudo().search([('id', '=', order.partner_id.id)])
    #
    #                 vals = {
    #                     'partner_id': partner.id,
    #                     'loyalty_id': order.wk_loyalty_program_id.id,
    #                     'points_processed': order.loyalty_points,
    #                     'pos_order_ref': order.id,
    #                     'loyalty_process': 'addition',
    #                     'process_reference': 'Pos Order',
    #                 }
    #                 history_obj = History.create(vals)
    #         if order.partner_id and  order.reward_redeem:
    #             History = self.env['website.loyalty.history']
    #             posorder_line = order.lines.filtered(
    #                 lambda line: line.product_id == order.wk_loyalty_program_id.product_id
    #             )
    #             if len(posorder_line):
    #                 pos_order_line = posorder_line[0]
    #                 domain = [
    #                     ('pos_order_ref', '=', order.id),
    #                     ('loyalty_process', '=', 'deduction')
    #                 ]
    #                 already_deducted = History.search_count(domain)
    #                 if not already_deducted:
    #                     vals = {
    #                         'loyalty_id':order.wk_loyalty_program_id.id,
    #                         'partner_id': order.partner_id.id,
    #                         'points_processed': abs(pos_order_line.price_unit),
    #                         'pos_order_ref': order.id,
    #                         'redeem_amount': pos_order_line.price_unit,
    #                         'loyalty_process': 'deduction',
    #                         'process_reference': 'Pos Order',
    #                     }
    #                     History.create(vals)
    #
    #         else:
    #             pass
    #
    #
    #     return order_ids

