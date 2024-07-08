from odoo import fields,models,api,_
from odoo.tests import Form


class PosSession(models.Model):
    _inherit = 'pos.session'

    paper_count = fields.Integer(string="Paper Cost", compute="_compute_paper_cost")

    @api.depends('state')
    def _compute_paper_cost(self):
        for session in self:
            session.paper_count = len(self.env['paper.cost'].sudo().search([('session_id', '=', session.id)]))

    def action_paper_view(self):
        tree_id = self.env.ref('pos_paper_cost.paper_cost_tree_view').id
        form_id = self.env.ref('pos_paper_cost.paper_cost_form_view').id
        search_id = self.env.ref('pos_paper_cost.paper_cost_search_view').id
        paper_ids = self.env['paper.cost'].sudo().search([('session_id', '=', self.id)])
        return {
            'type': 'ir.actions.act_window',
            'name': _('Paper Cost'),
            'view_mode': 'tree,form',
            'res_model': 'paper.cost',
            'domain': str([('id', 'in', paper_ids.ids)]),
            'views': [(tree_id, 'tree'), (form_id, 'form')],
            'search_view_id': search_id,
        }

    def _validate_session(self):
        res = super(PosSession, self)._validate_session()
        for session in self:
            data_dict = {}
            for order in session.order_ids.filtered(lambda x: x.delivery_type not in ['dine_in']):
                for order_line in order.lines:
                    if order_line.product_id.paper_size_id:
                        if order_line.product_id.paper_size_id.id in data_dict:
                            data_dict[order_line.product_id.paper_size_id.id]['qty'] += order_line.qty
                            data_dict[order_line.product_id.paper_size_id.id]['pos_order_ids'] += order.ids
                        else:
                            data_dict[order_line.product_id.paper_size_id.id] = {
                                'pos_order_ids': order.ids,
                                'product_id': order_line.product_id.paper_size_id,
                                'qty': order_line.qty
                            }
            for data in data_dict:
                qty = data_dict[data]['qty']
                product_id = data_dict[data]['product_id']
                pos_order_ids = data_dict[data]['pos_order_ids']

                val = {
                    'session_id': session.id,
                    'pos_order_ids': [(6, 0, pos_order_ids)],
                    'product_id': product_id.id,
                    'qty': qty,
                }
                paper_cost_id = self.env['paper.cost'].sudo().create(val)
                val = {
                    'user_id': False,
                    'picking_type_id': session.config_id.picking_type_id.id,
                    'move_type': 'direct',
                    'location_id': session.config_id.picking_type_id.default_location_src_id.id,
                    'location_dest_id': session.config_id.picking_type_id.default_location_dest_id.id,
                }
                new_picking_id = self.env['stock.picking'].sudo().create(val)
                stock_move_val = {
                    'name': product_id.name,
                    'product_uom': product_id.product_variant_id.uom_id.id,
                    'picking_id': new_picking_id.id,
                    'picking_type_id': new_picking_id.picking_type_id.id,
                    'product_id': product_id.product_variant_id.id,
                    'product_uom_qty': abs(qty),
                    'state': 'draft',
                    'location_id': new_picking_id.location_id.id,
                    'location_dest_id': new_picking_id.location_dest_id.id,
                    'company_id': new_picking_id.company_id.id,
                }
                new_move_id = self.env['stock.move'].sudo().create(stock_move_val)
                new_picking_id.action_confirm()
                if new_picking_id:
                    if new_picking_id.state == 'confirmed':
                        new_picking_id.action_assign()
                backorder_wiz = new_picking_id.button_validate()
                if backorder_wiz != True:
                    if backorder_wiz['res_model'] == 'confirm.stock.sms':
                        backorder_wiz = Form(self.env[backorder_wiz['res_model']].with_context(
                            backorder_wiz['context'])).save()
                        backorder_wiz.write(
                            {'pick_ids': [(4, p) for p in backorder_wiz._context['active_ids']]})
                        backorder_wiz.send_sms()

                    elif 'res_model' in backorder_wiz:
                        backorder_wiz = Form(self.env[backorder_wiz['res_model']].with_context(
                            backorder_wiz['context'])).save()
                        back_dict = backorder_wiz.process()

                        if back_dict != True:

                            if back_dict['res_model'] == 'confirm.stock.sms':
                                back_dict = Form(self.env[back_dict['res_model']].with_context(
                                    back_dict['context'])).save()
                                back_dict.write(
                                    {'pick_ids': [(4, p) for p in back_dict._context['active_ids']]})
                                back_dict.send_sms()

                            if back_dict['res_model'] == 'stock.backorder.confirmation':
                                back_dict = Form(self.env[back_dict['res_model']].with_context(
                                    back_dict['context'])).save()
                                back_dict_2 = back_dict.process()

                                if back_dict_2 != True:

                                    if back_dict_2['res_model'] == 'confirm.stock.sms':
                                        back_dict_2 = Form(
                                            self.env[back_dict_2['res_model']].with_context(
                                                back_dict_2['context'])).save()
                                        back_dict_2.write({'pick_ids': [(4, p) for p in
                                                                        back_dict_2._context[
                                                                            'active_ids']]})
                                        back_dict_2.send_sms()
        return res

