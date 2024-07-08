
import logging

from odoo import api, fields, models,_
import odoo.addons.decimal_precision as dp
from odoo.exceptions import Warning

_logger = logging.getLogger(__name__)

State = [
    ('draft', 'Draft'),
    ('done', 'Done'),
    ('cancel', 'Cancel')
]


class ResPartner(models.Model):
    _inherit = 'res.partner'

    wk_website_loyalty_points = fields.Float(
        string='Website Loyalty Points',
        help='The points are the points with which the user is awarded of being Loyal !',
        digits=dp.get_precision('Loyalty Points'),
        default=0,
        compute='_compute_loyalty_points',
        store=False

    )

    def _compute_loyalty_points(self):
        for record in self:
            domain = [
                ('partner_id', '=', record.id),
            ]
            credit = 0
            debit = 0
            histories = self.env['website.loyalty.history'].sudo().search(domain)
            for history in histories:
                if history.loyalty_process == 'addition':
                    credit += history.points_processed
                else:
                    debit += history.points_processed
            points = credit - debit
            record.wk_website_loyalty_points = round(points)



class res_users(models.Model):
    _inherit = 'res.users'

    wk_website_loyalty_points = fields.Float(
        related='partner_id.wk_website_loyalty_points'
    )

    @api.model
    def create(self, vals):
        ir_model_data = self.env['ir.model.data']
        portal_user_id = ir_model_data.get_object_reference(
            'base', 'group_portal')[1]
        wk_loyalty_program_id = self.env['website'].sudo().get_current_website().wk_loyalty_program_id
        groups_id = vals.get('groups_id')
        portal_signup = (self.env.ref('base.group_portal').id in groups_id[0]) if groups_id else False
        if wk_loyalty_program_id  and (portal_signup or vals.get('in_group_1')):
            wk_website_loyalty_points = wk_loyalty_program_id._fetch_signup_loyalty_points()
            if wk_website_loyalty_points:
                vals['wk_website_loyalty_points'] = wk_website_loyalty_points
                res = super(res_users, self).create(vals)
                res.partner_id.wk_website_loyalty_points =wk_website_loyalty_points
                history_vals = {
                    'partner_id': res.partner_id.id,
                    'loyalty_id': wk_loyalty_program_id.id,
                    'points_processed': wk_website_loyalty_points,
                    'loyalty_process': 'addition',
                    'process_reference': 'Sign Up',
                }

                self.env['website.loyalty.history'].sudo().create(history_vals)
                return res
        return super(res_users, self).create(vals)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    loyalty_id = fields.Many2one('website.loyalty.history')
    def unlink(self):
        for line in self:
            if line.loyalty_id:
                line.loyalty_id.unlink()
        res=super(SaleOrderLine, self).unlink()
        return res

    def write(self, vals):
        res = super(SaleOrderLine, self).write(vals)
        for i in  self:
            if not i._context.get('loyalty',False):
                if i.loyalty_id:
                    i.with_context(loyalty=True).price_unit=0

        return res


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def create(self, vals_list):
        res = super(SaleOrder, self).create(vals_list)
        if not res.wk_loyalty_program_id:
            wk_loyalty_program_id= self.env['website'].get_current_website().wk_loyalty_program_id.id
            res.wk_loyalty_program_id= wk_loyalty_program_id
        return res

    @api.depends('order_line.price_total')
    def _compute_wk_website_loyalty_points(self):
        for order in self:
            if order.wk_loyalty_state not in ['cancel', 'done']:
                amount = order.amount_total
                obj = self.env['website'].get_current_website().wk_loyalty_program_id
                if obj:
                    wk_website_loyalty_points = order.wk_extra_loyalty_points + obj.get_loyalty_points(amount)
                    order.update({
                        'wk_website_loyalty_points': wk_website_loyalty_points,
                    })
                else:
                    order.update({
                        'wk_website_loyalty_points': 0.0,
                    })
    @api.model
    def _get_default_wk_loyalty_program_id(self):
        return self.env['website'].sudo().get_current_website().wk_loyalty_program_id.id


    wk_extra_loyalty_points = fields.Float(
        string='Extra Loyalty Points',
        copy=False,
        default=0
    )
    wk_loyalty_program_id = fields.Many2one(
        string = 'Loyalty Program',
        comodel_name = 'website.loyalty.management',
        default = _get_default_wk_loyalty_program_id
    )
    wk_website_loyalty_points = fields.Float(
        string='Loyalty Points',
        store=True,
        readonly=True,
        compute='_compute_wk_website_loyalty_points'
    )
    wk_loyalty_state = fields.Selection(
        selection=State,
        string='Loyalty Stage',
        default='draft',
        copy=False
    )


    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        self.wk_loyalty_program_id= self.env['website'].sudo().get_current_website().wk_loyalty_program_id.id
        for record in self.filtered('wk_loyalty_program_id'):
            loyalty_obj = record.wk_loyalty_program_id
            loyalty_obj.update_partner_loyalty(record,'confirm')
        return res

    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        for record in self.filtered('wk_loyalty_program_id'):
            loyalty_obj = record.wk_loyalty_program_id
            loyalty_obj.cancel_redeem_history(record)
        return res
