import datetime
from odoo import models, api, fields, _
from datetime import timedelta
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta


class POSSessionConfig(models.Model):
    _inherit = 'pos.config'


    def open_existing_session_cb(self):
        """ close session button

        access session form to validate entries
        """

        if self.current_session_id.state == 'opening_control':
            self.ensure_one()
            return self._open_session(self.current_session_id.id)
        if self.current_session_id.state == 'closing_control' or self.current_session_id.state == 'opened':
            self.current_session_id.action_pos_session_closing_control_inherited()
            self.ensure_one()

    def open_session_cb_new(self, check_coa=True):
        """ new session button

        create one if none exist
        access cash control interface if enabled or start a session
        """
        self.ensure_one()
        # if not self.current_session_id:
        self._check_company_journal()
        self._check_company_invoice_journal()
        self._check_company_payment()
        self._check_currencies()
        self._check_profit_loss_cash_journal()
        self._check_payment_method_ids()
        self._check_payment_method_receivable_accounts()
        new_session = self.env['pos.session'].create({
            'user_id': self.env.uid,
            'config_id': self.id
        })
        new_session.write({
            'state': 'opened'
        })
        return self.open_ui()

    def open_ui_not_started(self):
        """Open the pos interface with config_id as an extra argument.

        In vanilla PoS each user can only have one active session, therefore it was not needed to pass the config_id
        on opening a session. It is also possible to login to sessions created by other users.

        :returns: dict
        """
        if self.current_session_id.state == 'opening_control':
            self.current_session_id.write({
                'state': 'opened'
            })
        self.ensure_one()
        # check all constraints, raises if any is not met
        self._validate_fields(set(self._fields) - {"cash_control"})
        return {
            'type': 'ir.actions.act_url',
            'url': self._get_pos_base_url() + '?config_id=%d' % self.id,
            'target': 'self',
        }
class PosSessionSummarys(models.Model):
    _inherit = 'pos.session.summary'

    petty_cash_pull_out = fields.Float('Petty cash pull out')
    bank_deposit_variance = fields.Float(string='Bank deposit variance')
    insert_bag_number = fields.Char('Insert Bag Number')
    status = fields.Selection([
        ('dropped', 'Dropped'),
        ('approved', 'Approved'),
    ], string='Status', default='dropped')


    approve_status = fields.Boolean("Collection approved")

    def get_date(self):

        date_today = datetime.now()
        dates = {'date_today': date_today}
        return dates

    @api.onchange('approve_status')
    def set_cash_collection_status(self):
        for rec in self:
            if rec.approve_status == True:
                rec.status = 'approved'
            if rec.approve_status == False:
                rec.status = 'dropped'

class PosSession(models.Model):
    _inherit = 'pos.session'

    session_summary = fields.Many2one('pos.session.summary')
    session_summary_boolean = fields.Boolean('pos.session.summary')

    def open_frontend_cb(self):
        """Open the pos interface with config_id as an extra argument.

        In vanilla PoS each user can only have one active session, therefore it was not needed to pass the config_id
        on opening a session. It is also possible to login to sessions created by other users.

        :returns: dict
        """
        if self.state == 'opening_control':
            self.write({
                'state': 'opened'
            })
        if not self.ids:
            return {}
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.config_id._get_pos_base_url() + '?config_id=%d' % self.config_id.id,
        }

    @api.constrains('config_id')
    def _check_pos_config(self):
        if self.search_count([
            ('state', 'not in', ['closed', 'closing_control']),
            ('config_id', '=', self.config_id.id),
            ('rescue', '=', False)
        ]) > 1:
            raise ValidationError(_("Another session is already opened for this point of sale."))

    def action_pos_session_closing_control_inherited(self):
        self._check_pos_session_balance()
        for session in self:
            if session.state == 'closed':
                raise UserError(_('This session is already closed.'))
            session.write({'state': 'closing_control', 'stop_at': fields.Datetime.now()})
            # if not session.config_id.cash_control:
            #     session.action_pos_session_close()

    def action_pos_session_closing_control(self):
        self._check_pos_session_balance()
        for session in self:
            if session.state == 'closed':
                raise UserError(_('This session is already closed.'))
            session.write({'state': 'closing_control', 'stop_at': fields.Datetime.now()})
            if not session.config_id.cash_control:
                session.action_pos_session_close()

    def _check_pos_session_balance(self):
        for session in self:
            for statement in session.statement_ids:
                if (statement != session.cash_register_id) and (statement.balance_end != statement.balance_end_real):
                    statement.write({'balance_end_real': statement.balance_end})

    def validate_pos_session_closing_control(self):
        print("validate_pos_session_closing_control")
        # data = self.load_session_details(self.id)
        # self.session_data_wizard(data)
        session_data = self.env['pos.employee.wizard']
        # closed_session = session_data.sudo().create(data)
        view_item = [(self.env.ref('pos_summary_backend.wizard_Employee_pin_wizard').id, 'form')]
        view = self.env.ref('pos_summary_backend.wizard_Employee_pin_wizard')
        # print("LLLLL", closed_session)
        return {
            'name': _('Please Enter Employee Pin'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'pos.employee.wizard',
            'views': view_item,
            'view_id': view.id,
            'target': 'new',
            'context': {
                'default_session': self.id,
            }
        }


    def load_session_details(self, current_session):
        lines = []
        data = {}
        session = self.env['pos.session'].sudo().search([('id', '=', int(current_session))])
        if session:
            orders = session.order_ids
            pos_orders = []
            total_cash = 0.0
            total_eftpos = 0.0
            total_discount = 0.0
            total_redeem = 0.0
            total_loyalty = 0.0
            total_tips = 0.0
            data['session'] = session.id
            data['cash_unit'] = session.company_id.currency_id.currency_unit_label
            data['cash_subunit'] = session.company_id.currency_id.currency_subunit_label
            data['session_user'] = session.user_id.id
            data['pos_config'] = session.config_id.id
            data['starting_balance'] = round(session.cash_register_balance_start, 2)
            data['opening_date'] = session.start_at
            data['total_payments_amount'] = session.total_payments_amount
            data['orders_count'] = session.order_count
            if orders:
                payments = self.env['pos.payment'].sudo().search([('session_id', '=', int(session.id))])
                for amount in payments:
                    if amount.payment_method_id.name == 'Cash':
                        total_cash = total_cash + amount.amount
                    else:
                        total_eftpos = total_eftpos + amount.amount
                for order in orders:
                    if order.reward_redeem_amount:
                        total_loyalty = total_loyalty + order.reward_redeem_amount
                    if order.redeem_card_amount:
                        total_redeem = total_redeem + order.redeem_card_amount
                    if order.lines:
                        for line in order.lines:
                            # if line.loyalty_points > 0:
                            #     total_loyalty = total_loyalty + line.loyalty_points
                            if line.full_product_name in ['discount', 'Discount']:
                                discount_amount = line.price_subtotal
                                total_discount = total_discount + discount_amount
                            if line.full_product_name == 'Tips':
                                total_tips = total_tips + line.price_subtotal_incl

            data['total_cash'] = round(total_cash, 2)
            data['total_eftpos'] = round(total_eftpos, 2)
            data['redeem_card_amount'] = round(total_redeem, 2)
            data['discount_amount'] = round(total_discount*-1, 2)
            data['loyalty_points_used'] = round(total_loyalty, 2)
            data['total_tips'] = round(total_tips, 2)
            data['float_amount'] = round(data['starting_balance'], 2)

            # data['cash_variance'] = 0 - round(total_cash, 2)
            data['cash_variance'] = -abs(round(0 - round(total_cash, 2) + 0 - round(data['starting_balance'], 2), 2))
            data['eftpos_variance'] = 0 - round(total_eftpos, 2)
            data['total_variance'] = round(0 - round(total_eftpos, 2) + 0 - round(total_cash, 2), 2)

            data['total_expected'] = round(round(total_cash, 2) + round(total_eftpos, 2), 2)
            total = round(total_cash, 2) + round(total_eftpos, 2)
            # data['closing_date'] = session.stop_at
            data['journal_entries'] = session.move_id.id
            data['counted_eftpos'] = round(total_eftpos, 2)

        return data

    def action_pos_session_close(self):
        # Session without cash payment method will not have a cash register.
        # However, there could be other payment methods, thus, session still
        # needs to be validated.
        # summary = self.env['pos.session.summary'].search([('session','=',self.id)],limit=1)
        # if summary:
        #     raise ValidationError(_("Please close and validate session manually."))
        # else:
        if not self.cash_register_id:
            return self._validate_session()

        if self.cash_control and abs(self.cash_register_difference) > self.config_id.amount_authorized_diff:
            # Only pos manager can close statements with cash_register_difference greater than amount_authorized_diff.
            if not self.user_has_groups("point_of_sale.group_pos_manager"):
                raise UserError(_(
                    "Your ending balance is too different from the theoretical cash closing (%.2f), "
                    "the maximum allowed is: %.2f. You can contact your manager to force it."
                ) % (self.cash_register_difference, self.config_id.amount_authorized_diff))
            else:
                return self._warning_balance_closing()
        else:
            return self._validate_session()