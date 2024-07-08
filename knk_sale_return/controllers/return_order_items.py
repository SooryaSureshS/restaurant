from odoo import http
from odoo.http import request


class ReturnOrder(http.Controller):

    @http.route('/my/order/return', type='json', auth='public')
    def return_order(self, **kwargs):
        order_id = int(kwargs.get('order_id'))
        order = request.env['sale.order'].sudo().browse(order_id)
        lines = kwargs.get('lines')
        lines = {int(k): int(v) for (k, v) in lines.items() if v != ''}
        if lines:
            todo_return_lines = []
            return_id = request.env['sale.order.return'].sudo().search([('state', '=', 'confirm'),
                                                                        ('knk_sale_order_id', '=', order_id)],
                                                                       limit=1)
            for line in lines:
                line_id = request.env['sale.order.line'].sudo().browse(line)
                if return_id:
                    return_lines = return_id.knk_sale_order_return_line_ids.filtered(
                        lambda x: x.knk_product_id == lines[line])
                    if return_lines and (
                            sum(return_lines.mapped('knk_product_qty')) + lines[line]) > line_id.product_uom_qty:
                        return {'success': False,
                                'message': 'Quantity to be returned is greater than actual ordered quantity!'}
                    elif return_lines and (
                            sum(return_lines.mapped('knk_product_qty')) + lines[line]) <= line_id.product_uom_qty:
                        todo_return_lines.append({'pid': line, 'qty': lines[line]})
                    elif not return_lines and lines[line] > line_id.product_uom_qty:
                        return {'success': False,
                                'message': 'Quantity to be returned is greater than actual ordered quantity!'}
                    elif not return_lines and lines[line] <= line_id.product_uom_qty:
                        todo_return_lines.append({'pid': line, 'qty': lines[line]})

                else:
                    return_id = request.env['sale.order.return'].sudo().create({
                        'partner_id': order.partner_id.id,
                        'knk_sale_order_id': order_id
                    })
                    if lines[line] <= line_id.product_uom_qty:
                        todo_return_lines.append({'pid': line, 'qty': lines[line]})
                    else:
                        return {'success': False,
                                'message': 'Quantity to be returned is greater than actual ordered quantity!'}
            for line in todo_return_lines:
                request.env['sale.order.return.line'].sudo().create({
                    'knk_sale_return_id': return_id.id,
                    'knk_product_id': line['pid'],
                    'knk_product_qty': line['qty'],
                })
            return {'success': True, 'message': 'Order returned successfully'}
        return {'success': False, 'message': 'Atleast one product need to be returned!'}
