from odoo import models, api, fields, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round
from odoo.addons.account.models.account_move import AccountMoveLine


def unlink(self):
    moves = self.mapped('move_id')

    # Prevent deleting lines on posted entries
    if not self.env.context.get('force_delete', False) and any(m.state == 'posted' for m in moves):
        raise UserError(_('You cannot delete an item linked to a posted entry.'))

    # Check the lines are not reconciled (partially or not).
    self._check_reconciliation()

    # Check the lock date.
    moves._check_fiscalyear_lock_date()

    # Check the tax lock date.
    self._check_tax_lock_date()

    res = super(AccountMoveLine, self).unlink()
    moves._recompute_dynamic_lines(recompute_all_taxes=False)
    # Check total_debit == total_credit in the related moves.
    if self._context.get('check_move_validity', True):
        moves._check_balanced()

    return res


AccountMoveLine.unlink = unlink


class PosOrderReturn(models.Model):
    _inherit = 'pos.order'

    return_ref = fields.Char(string='Return Ref', readonly=True, copy=False)
    return_status = fields.Selection([
        ('nothing_return', 'Nothing Returned'),
        ('partialy_return', 'Partialy Returned'),
        ('fully_return', 'Fully Returned')
    ], string="Return Status", default='nothing_return',
        readonly=True, copy=False, help="Return status of Order")

    @api.model
    def get_lines(self, ref):
        result = []
        order_id = self.search([('pos_reference', '=', ref)], limit=1)
        if order_id:
            lines = self.env['pos.order.line'].search([('order_id', '=', order_id.id)])
            for line in lines:
                if line.qty - line.returned_qty > 0:
                    new_vals = {
                        'product_id': line.product_id.id,
                        'product': line.product_id.name,
                        'qty': line.qty - line.returned_qty,
                        'price_unit': line.price_unit,
                        'discount': line.discount,
                        'line_id': line.id,
                    }
                    result.append(new_vals)

        return [result]

    #
    def _order_fields(self, ui_order):
        order = super(PosOrderReturn, self)._order_fields(ui_order)
        if 'return_ref' in ui_order.keys() and ui_order['return_ref']:
            order['return_ref'] = ui_order['return_ref']
            parent_order = self.search([('pos_reference', '=', ui_order['return_ref'])], limit=1)

            updated_lines = ui_order['lines']

            ret = 0
            qty = 0
            for uptd in updated_lines:
                line = self.env['pos.order.line'].search([('order_id', '=', parent_order.id),
                                                          ('id', '=', uptd[2]['line_id'])], limit=1)
                if line:
                    line.returned_qty += -(uptd[2]['qty'])
            for line in parent_order.lines:
                qty += line.qty
                ret += line.returned_qty
            if qty - ret == 0:
                if parent_order:
                    parent_order.return_status = 'fully_return'
            elif ret:
                if qty > ret:
                    if parent_order:
                        parent_order.return_status = 'partialy_return'
        return order

    @api.model
    def get_pos_order(self, pos_order_days):
        import datetime
        from dateutil.relativedelta import relativedelta
        day = (datetime.datetime.now() - relativedelta(days=pos_order_days)).strftime('%Y-%m-%d')
        orders = self.search([('date_order', '>=', day)])
        list_order = []
        for i in orders:
            data = {
                'name': i.name,
                'partner_id': [i.partner_id.id or False, i.partner_id.name or False],
                'date_order': i.date_order,
                'amount_total': i.amount_total,
                'amount_tax': i.amount_tax,
                'pos_reference': i.pos_reference,
                'lines': i.lines,
                'state': i.state,
                'session_id': i.session_id.id,
                'company_id': i.company_id.id,
                'return_ref': i.return_ref,
                'return_status': i.return_status
            }
            list_order.append(data)
        return list_order


class PosOrderLineReturn(models.Model):
    _inherit = 'pos.order.line'

    returned_qty = fields.Integer(string='Returned Qty', digits=0, readonly=True)


class SaleDataOrderLineReturn(models.Model):
    _inherit = 'sale.order'

    return_ref = fields.Char(string='Return Ref', readonly=True, copy=False)
    return_status = fields.Selection([
        ('nothing_return', 'Nothing Returned'),
        ('partialy_return', 'Partialy Returned'),
        ('fully_return', 'Fully Returned')
    ], string="Return Status", default='nothing_return',
        readonly=True, copy=False, help="Return status of Order")

    @api.model
    def get_sale_order(self, sale_order_days):
        import datetime
        from dateutil.relativedelta import relativedelta
        day = (datetime.datetime.now() - relativedelta(days=sale_order_days)).strftime('%Y-%m-%d')
        orders = self.search(
            [('date_order', '>=', day), ('state', '=', 'sale'), ('return_status', '!=', 'fully_return')])
        list_order = []
        for i in orders:
            list_order_line = []
            for line in i.order_line:
                new_vals = {
                    'product_id': line.product_id.id,
                    'product': line.product_id.name,
                    'qty': line.product_uom_qty - line.returned_qty,
                    'price_unit': line.price_unit,
                    'discount': line.discount,
                    'line_id': line.id,
                    'price_total': line.price_total,
                }
                list_order_line.append(new_vals)
            data = {
                'name': i.name,
                'partner_id': [i.partner_id.id or False, i.partner_id.name or False],
                'date_order': i.date_order,
                'amount_total': i.amount_total,
                'amount_tax': i.amount_tax,
                'order_line': i.order_line,
                'state': i.state,
                'id': i.id,
                'return_status': dict(self._fields['return_status'].selection).get(
                    i.return_status) if i.return_status else '',
                'lines': list_order_line

            }
            list_order.append(data)
        return list_order

    @api.model
    def get_lines(self, ref):
        result = []
        order_id = self.search([('id', '=', ref)], limit=1)
        if order_id:
            lines = self.env['sale.order.line'].search([('order_id', '=', order_id.id)])
            for line in lines:
                if line.product_uom_qty - line.returned_qty > 0:
                    new_vals = {
                        'product_id': line.product_id.id,
                        'product': line.product_id.name,
                        'qty': line.product_uom_qty - line.returned_qty,
                        'price_unit': line.price_unit,
                        'discount': line.discount,
                        'line_id': line.id,
                    }
                    result.append(new_vals)

        return [result]

    @api.model
    def set_amount_product(self, order, total_amount):
        sale_order = self.env['sale.order'].sudo().browse([int(order)])
        if sale_order:
            if sale_order.return_status != 'fully_return' and float(total_amount) > 0:
                import stripe

                if sale_order.transaction_ids:
                    transaction_id = sale_order.transaction_ids[0]
                    if transaction_id.state == 'done' and transaction_id.acquirer_id.provider == 'stripe' and transaction_id.acquirer_id.stripe_secret_key:
                        stripe.api_key = transaction_id.acquirer_id.stripe_secret_key
                        try:
                            refund = stripe.Refund.create(
                                amount=int(float(total_amount) * 100),
                                payment_intent=transaction_id.stripe_payment_intent,
                            )
                        except Exception as e:
                            return [{"status": e}]
                        if refund['status'] == 'succeeded':
                            move_ids = sale_order.invoice_ids.filtered(lambda r: r.move_type in ['out_invoice'])
                            if move_ids:

                                move_reversal = self.env['account.move.reversal'].with_context(
                                    active_model="account.move",
                                    active_ids=move_ids.ids).create({
                                    'date': fields.Date.today(),
                                    'reason': 'Refund order to the customer',
                                    'refund_method': 'refund',
                                })
                                reversal = move_reversal.reverse_moves()
                                reverse_move = self.env['account.move'].browse(reversal['res_id'])
                                flag = 0
                                for line in reverse_move.invoice_line_ids:
                                    if flag != 0:
                                        line.with_context(check_move_validity=False).unlink()

                                    else:
                                        line.with_context(check_move_validity=False).write(
                                            ({'price_unit': float(total_amount)}))
                                    flag = flag + 1
                                reverse_move.action_post()
                                payment = self.env['account.payment.register'] \
                                    .with_context(active_model='account.move', active_ids=reverse_move.ids) \
                                    .create({'journal_id': sale_order.transaction_ids[0].acquirer_id.journal_id.id,
                                             'amount': reverse_move.amount_total,
                                             'payment_method_id': self.env.ref(
                                                 'account.account_payment_method_manual_in').id,
                                             }) \
                                    ._create_payments()

                                out_refund = sale_order.invoice_ids.filtered(lambda r: r.move_type in ['out_refund'])
                                if out_refund:
                                    if sum(out_refund.mapped('amount_total')) == sale_order.amount_total:
                                        sale_order.return_status = 'fully_return'
                                    else:
                                        sale_order.return_status = 'partialy_return'

                                return [{"status": "Payment Refunded successfully"}]
                        else:
                            return [{"status": "Something went wrong!!! Please try again Later!!"}]
                    else:
                        return [{"status": "Payment not Registered For this Order"}]
                else:
                    return [{"status": "Payment not Registered For this Order"}]
            else:
                if sale_order.return_status != 'fully_return':
                    return [{"status": "Amount is already Returned!!"}]
                else:
                    return [{"status": "Order Not found!!"}]

        else:
            return [{"status": "Something Went Wrong!! Please Try Again Later"}]

    @api.model
    def set_return_product(self, list):
        amount = 0
        sale_order = ''
        line_ids = []
        for rec in list:
            sale_order_line = self.env['sale.order.line'].sudo().browse([rec['line_id']])
            if sale_order_line.invoice_status == 'invoiced' and float(
                    rec['return_qty']) <= sale_order_line.qty_invoiced:
                price = sale_order_line.price_total / sale_order_line.product_uom_qty
                amount = amount + (price * int(rec['return_qty']))
                line_ids.append(rec)
                if sale_order == '':
                    sale_order = sale_order_line.order_id
            else:
                if sale_order_line and sale_order == '':
                    sale_order = sale_order_line.order_id
        if sale_order == '':
            return [{"status": "Something Went Wrong!! Please Try Again Later"}]

        if sale_order.return_status != 'fully_return' and amount > 0:
            import stripe
            if sale_order.transaction_ids:
                transaction_id = sale_order.transaction_ids[0]
                if transaction_id.state == 'done' and transaction_id.acquirer_id.provider == 'stripe' and transaction_id.acquirer_id.stripe_secret_key:
                    stripe.api_key = transaction_id.acquirer_id.stripe_secret_key
                    try:
                        refund = stripe.Refund.create(
                            amount=round(amount) * 100,
                            payment_intent=transaction_id.stripe_payment_intent,
                        )
                    except Exception as e:
                        return [{"status": e}]
                    if refund:
                        if refund['status'] == 'succeeded':
                            try:
                                self.sale_refund_order(sale_order, line_ids)
                                if len(line_ids) == len(sale_order.order_line):
                                    sale_order.return_status = 'fully_return'
                                else:
                                    sale_order.return_status = 'partialy_return'

                                return [{"status": "Payment Refunded successfully"}]
                            except:
                                return [{"status": "Payment Refunded Failed"}]
                        else:
                            return [{"status": "Payment Refunded Failed"}]
                    else:
                        return [{"status": "Payment Refunded Failed"}]
                return [{"status": "Payment not Registered For this Order"}]
            else:
                return [{"status": "No Transaction for this Order"}]
        else:
            if sale_order.return_status == 'fully_return':
                return [{"status": "Order Is Already Refunded"}]
            elif not sale_order.transaction_ids:
                return [{"status": "No Transaction for this Order"}]
            else:
                return [{"status": "Nothing To Refund Or Its Already Refunded"}]

    @api.model
    def _prepare_stock_return_picking_line_vals_from_move(self, stock_move):
        quantity = stock_move.product_qty
        for move in stock_move.move_dest_ids:
            if move.origin_returned_move_id and move.origin_returned_move_id != stock_move:
                continue
            if move.state in ('partially_available', 'assigned'):
                quantity -= sum(move.move_line_ids.mapped('product_qty'))
            elif move.state in ('done'):
                quantity -= move.product_qty
        quantity = float_round(quantity, precision_rounding=stock_move.product_uom.rounding)
        return {
            'product_id': stock_move.product_id.id,
            'quantity': quantity,
            'move_id': stock_move.id,
            'uom_id': stock_move.product_id.uom_id.id,
        }

    @api.model
    def sale_refund_order(self, sale_order, line_ids):
        picking_line = []
        picking_id = ''
        values = {}

        for rec in line_ids:
            sale_order_line = self.env['sale.order.line'].sudo().browse([rec['line_id']])
            move_ids = sale_order_line.move_ids.filtered(lambda r: r.picking_type_id.sequence_code in ['OUT'])
            if move_ids:
                if picking_id == '':
                    picking_id = move_ids[0].picking_id
                vals = self._prepare_stock_return_picking_line_vals_from_move(move_ids[0])
                vals['quantity'] = rec['return_qty']
                picking_line.append((0, 0, vals))

        values[
            'parent_location_id'] = picking_id.picking_type_id.warehouse_id and picking_id.picking_type_id.warehouse_id.view_location_id.id or self.picking_id.location_id.location_id.id
        values['original_location_id'] = picking_id.location_id.id
        location_id = picking_id.location_id.id
        if picking_id.picking_type_id.return_picking_type_id.default_location_dest_id.return_location:
            location_id = picking_id.picking_type_id.return_picking_type_id.default_location_dest_id.id
        values['location_id'] = location_id
        values['product_return_moves'] = picking_line
        values['picking_id'] = picking_id.id

        create_return_picking = self.env['stock.return.picking'].sudo().create(values)

        new_picking_id, pick_type_id = create_return_picking._create_returns()
        new_picking_id = self.env['stock.picking'].sudo().browse([new_picking_id])
        new_picking_id.action_assign()
        new_picking_id.action_confirm()
        for mv in new_picking_id.move_ids_without_package:
            mv.quantity_done = mv.product_uom_qty
        new_picking_id.button_validate()

        wiz = self.env['sale.advance.payment.inv'].with_context(active_ids=sale_order.ids, open_invoices=True).create(
            {'advance_payment_method': 'delivered'})
        invoice = wiz.with_context(pos_return_pos=True).create_invoices()
        invoice.action_post()

        payment = self.env['account.payment.register'] \
            .with_context(active_model='account.move', active_ids=invoice.ids) \
            .create(
            {'journal_id': sale_order.transaction_ids[0].acquirer_id.journal_id.id, 'amount': invoice.amount_total,
             'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
             }) \
            ._create_payments()
        return True


class PosOrderLineReturn(models.Model):
    _inherit = 'sale.order.line'

    returned_qty = fields.Integer(string='Returned Qty', digits=0, readonly=True)


class PosOrderConfigurationReturn(models.Model):
    _inherit = 'pos.config'

    return_order = fields.Boolean(string='Return Order', default=True)
    pos_order_days = fields.Integer(string='Pos Order Before ', default=10)
    sale_order_days = fields.Integer(string='Sale Order Before', default=10)


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def create_invoices(self):
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))

        if self.advance_payment_method == 'delivered':
            inv = sale_orders._create_invoices(final=self.deduct_down_payments)
        else:
            inv = False
            # Create deposit product if necessary
            if not self.product_id:
                vals = self._prepare_deposit_product()
                self.product_id = self.env['product.product'].create(vals)
                self.env['ir.config_parameter'].sudo().set_param('sale.default_deposit_product_id', self.product_id.id)

            sale_line_obj = self.env['sale.order.line']
            for order in sale_orders:
                amount, name = self._get_advance_details(order)

                if self.product_id.invoice_policy != 'order':
                    raise UserError(
                        _('The product used to invoice a down payment should have an invoice policy set to "Ordered quantities". Please update your deposit product to be able to create a deposit invoice.'))
                if self.product_id.type != 'service':
                    raise UserError(
                        _("The product used to invoice a down payment should be of type 'Service'. Please use another product or update this product."))
                taxes = self.product_id.taxes_id.filtered(
                    lambda r: not order.company_id or r.company_id == order.company_id)
                tax_ids = order.fiscal_position_id.map_tax(taxes, self.product_id, order.partner_shipping_id).ids
                analytic_tag_ids = []
                for line in order.order_line:
                    analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids]

                so_line_values = self._prepare_so_line(order, analytic_tag_ids, tax_ids, amount)
                so_line = sale_line_obj.create(so_line_values)
                self._create_invoice(order, so_line, amount)
        if self._context.get('open_invoices', False):
            if self._context.get('pos_return_pos', False):
                return inv
            else:

                return sale_orders.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}
