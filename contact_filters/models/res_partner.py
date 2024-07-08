from odoo import models, fields, api, _
import logging
from datetime import date
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError, ValidationError


# MASS_MAILING_BUSINESS_MODELS = [
#     'crm.lead',
#     'event.registration',
#     'hr.applicant',
#     'res.partner',
#     'event.track',
#     'sale.order',
#     'mailing.list',
#     'mailing.contact',
# ]
#
#
# class MassMailing(models.Model):
#     """ MassMailing models a wave of emails for a mass mailign campaign.
#     A mass mailing is an occurence of sending emails. """
#     _inherit = 'mailing.mailing'
#
#     mailing_model_id = fields.Many2one(
#         'ir.model', string='Recipients Model', ondelete='cascade', required=True,
#         domain=[('model', 'in', MASS_MAILING_BUSINESS_MODELS)],
#         default=lambda self: self.env.ref('mass_mailing.model_mailing_list').id)


class Loyalist(models.Model):
    _name = 'loyalist.contacts'

    name = fields.Char()
    email = fields.Char()
    phone = fields.Char()
    mobile = fields.Char()
    loyalist_contacts_id = fields.Many2one()


class Guest(models.Model):
    _name = 'guest.contacts'

    name = fields.Char()
    email = fields.Char()
    phone = fields.Char()
    mobile = fields.Char()
    guest_contacts_id = fields.Many2one()


# class NotPurchaseIn30Days(models.Model):
#     _name = 'not.purchase.thirty.d'
#
#     name = fields.Char()
#     email = fields.Char()
#     phone = fields.Char()
#     mobile = fields.Char()
#     partner_id = fields.Many2one()
#
#
# class NotPurchaseIn60Days(models.Model):
#     _name = 'not.purchase.sixty.d'
#
#     name = fields.Char()
#     email = fields.Char()
#     phone = fields.Char()
#     mobile = fields.Char()
#     partner_id = fields.Many2one()
#
#
# class NotPurchaseIn90Days(models.Model):
#     _name = 'not.purchase.ninety.d'
#
#     name = fields.Char()
#     email = fields.Char()
#     phone = fields.Char()
#     mobile = fields.Char()
#     partner_id = fields.Many2one()
#
#
# class OrderdPickupOnly(models.Model):
#     _name = 'order.pickup.only'
#
#     name = fields.Char()
#     email = fields.Char()
#     phone = fields.Char()
#     mobile = fields.Char()
#     partner_id = fields.Many2one()
#
#
# class OrderdDeliveryOnly(models.Model):
#     _name = 'order.delivery.only'
#
#     name = fields.Char()
#     email = fields.Char()
#     phone = fields.Char()
#     mobile = fields.Char()
#     partner_id = fields.Many2one()

#
# class CouponPurchase(models.Model):
#     _name = 'use.coupon.purchase'
#
#     name = fields.Char()
#     email = fields.Char()
#     phone = fields.Char()
#     mobile = fields.Char()
#     partner_id = fields.Many2one()

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # loyalist_contacts = fields.Many2one(string="loyalist contacts")
    # loyalist_boolean = fields.Boolean(string="Loyalist Boolean")

    sale_order_count = fields.Integer(compute='_compute_sale_order_count',
                                      string='count of Sales Order', store=True)
    loyalist_contacts = fields.One2many('loyalist.contacts', 'loyalist_contacts_id')
    guest_contacts = fields.One2many('guest.contacts', 'guest_contacts_id')

    # purchased_date = fields.Datetime(compute="_compute_purchase_date",string="purchase date",store=True)
    #
    # @api.depends('sale_order_ids.date_order')
    # def _compute_purchase_date(self):
    #     return {'domain': {
    #         'purchased_date': [('start_datetime', '>=', self.start_datetime), ('end_datetime', '<=', self.end_datetime)]}}

    # not_purchased_30_days = fields.One2many('not.purchase.thirty.d', 'partner_id')
    # not_purchased_60_days = fields.One2many('not.purchase.sixty.d', 'partner_id')
    # not_purchased_90_days = fields.One2many('not.purchase.ninety.d', 'partner_id')
    # order_pickup_only = fields.One2many('order.pickup.only', 'partner_id')
    # order_delivery_only = fields.One2many('order.delivery.only', 'partner_id')
    # used_a_coupon_to_purchase = fields.One2many('use.coupon.purchase', 'partner_id')

    def click_btn_contact(self):
        self.get_loyalist_accounts()
        self.get_guest_accounts()
        # self.get_not_purchase_in_30_days()
        # self.get_not_purchase_in_60_days()
        # self.get_not_purchase_in_90_days()
        # self.get_order_pickup_only()
        # self.get_order_delivery_only()
        # self.get_use_coupon_purchase()
        # return True

    # def get_use_coupon_purchase(self):
    #     partners = self.search([])
    #     for i in partners:
    #         if i.sale_order_ids.applied_coupon_ids:
    #             self.env['use.coupon.purchase'].create({'partner_id': i.id,
    #                                                 'name': i.name,
    #                                                 'phone': i.phone,
    #                                                 'mobile': i.mobile})

    # def get_not_purchase_in_30_days(self):
    #     thirty_days = date.today() - relativedelta(days=30)
    #     partners = self.search([('sale_order_ids.date_order', '<=', thirty_days)])
    #
    #     for i in partners:
    #         self.env['not.purchase.thirty.d'].create({'partner_id': i.id,
    #                                                   'name': i.name,
    #                                                   'phone': i.phone,
    #                                                   'mobile': i.mobile})
    #
    # def get_not_purchase_in_60_days(self):
    #     sixty_days = date.today() - relativedelta(days=60)
    #     partners = self.search([('sale_order_ids.date_order', '<=', sixty_days)])
    #     for i in partners:
    #         self.env['not.purchase.sixty.d'].create({'partner_id': i.id,
    #                                                  'name': i.name,
    #                                                  'phone': i.phone,
    #                                                  'mobile': i.mobile})
    #
    # def get_not_purchase_in_90_days(self):
    #     ninety_days = date.today() - relativedelta(days=90)
    #     partners = self.search([('sale_order_ids.date_order', '<=', ninety_days)])
    #     for i in partners:
    #         self.env['not.purchase.ninety.d'].create({'partner_id': i.id,
    #                                                   'name': i.name,
    #                                                   'phone': i.phone,
    #                                                   'mobile': i.mobile})

    def get_loyalist_accounts(self):
        loyalist = self.env['loyalist.contacts'].search([])
        loyalist_partners = self.search([('user_ids', '!=', False)])
        if len(loyalist) != len(loyalist_partners):
            for i in loyalist_partners:
                self.env['loyalist.contacts'].create({'loyalist_contacts_id': i.id,
                                                      'name': i.name,
                                                      'phone': i.phone,
                                                      'mobile': i.mobile})

    def get_guest_accounts(self):
        loyalist = self.env['guest.contacts'].search([])
        guest_partners = self.search([('user_ids', '=', False)])
        if len(loyalist) != len(guest_partners):
            for i in guest_partners:
                self.env['guest.contacts'].create({'guest_contacts_id': i.id,
                                                   'name': i.name,
                                                   'phone': i.phone,
                                                   'mobile': i.mobile})
    #
    # def get_order_pickup_only(self):
    #     partners = self.search([('sale_order_ids.website_delivery_type', '=', 'pickup'),
    #                             ('sale_order_ids.state', 'not in', ('draft', 'sent', 'cancel'))])
    #     for i in partners:
    #         self.env['order.pickup.only'].create({'partner_id': i.id,
    #                                               'name': i.name,
    #                                               'phone': i.phone,
    #                                               'mobile': i.mobile})
    #
    # def get_order_delivery_only(self):
    #     partners = self.search([('sale_order_ids.website_delivery_type', '=', 'delivery'),
    #                             ('sale_order_ids.state', 'not in', ('draft', 'sent', 'cancel'))])
    #     for i in partners:
    #         self.env['order.delivery.only'].create({'partner_id': i.id,
    #                                                 'name': i.name,
    #                                                 'phone': i.phone,
    #                                                 'mobile': i.mobile})




# class MergeInherit(models.TransientModel):
#     _inherit = 'base.partner.merge.automatic.wizard'
#
#     def _merge(self, partner_ids, dst_partner=None, extra_checks=True):
#         if self.env.is_admin():
#             extra_checks = False
#
#         Partner = self.env['res.partner']
#         partner_ids = Partner.browse(partner_ids).exists()
#         if len(partner_ids) < 2:
#             return
#
#         if len(partner_ids) > 3:
#             raise UserError(
#                 _("For safety reasons, you cannot merge more than 3 contacts together. You can re-open the wizard several times if needed."))
#
#         # check if the list of partners to merge contains child/parent relation
#         child_ids = self.env['res.partner']
#         for partner_id in partner_ids:
#             child_ids |= Partner.search([('id', 'child_of', [partner_id.id])]) - partner_id
#         if partner_ids & child_ids:
#             raise UserError(_("You cannot merge a contact with one of his parent."))
#
#         if extra_checks and len(set(partner.email for partner in partner_ids)) > 1:
#             raise UserError(
#                 _("All contacts must have the same email. Only the Administrator can merge contacts with different emails."))
#
#         # remove dst_partner from partners to merge
#         if dst_partner and dst_partner in partner_ids:
#             src_partners = partner_ids - dst_partner
#         else:
#             ordered_partners = self._get_ordered_partner(partner_ids.ids)
#             dst_partner = ordered_partners[-1]
#             src_partners = ordered_partners[:-1]
#         _logger.info("dst_partner: %s", dst_partner.id)
#
#         # FIXME: is it still required to make and exception for account.move.line since accounting v9.0 ?
#         if extra_checks and 'account.move.line' in self.env and self.env['account.move.line'].sudo().search(
#                 [('partner_id', 'in', [partner.id for partner in src_partners])]):
#             raise UserError(
#                 _("Only the destination contact may be linked to existing Journal Items. Please ask the Administrator if you need to merge several contacts linked to existing Journal Items."))
#
#         # Make the company of all related users consistent with destination partner company
#         if dst_partner.company_id:
#             partner_ids.mapped('user_ids').sudo().write({
#                 'company_ids': [(4, dst_partner.company_id.id)],
#                 'company_id': dst_partner.company_id.id
#             })
#
#         # call sub methods to do the merge
#         self._update_foreign_keys(src_partners, dst_partner)
#         self._update_reference_fields(src_partners, dst_partner)
#         self._update_values(src_partners, dst_partner)
#
#         self._log_merge_operation(src_partners, dst_partner)
#
#         # delete source partner, since they are merged
#         self.merge_contact_change(src_partners, dst_partner)
#         # src_partners.unlink()
#
#     def merge_contact_change(self, src_partners, dst_partner):
#         for src in src_partners:
#             src.pos_order_ids.partner_id = dst_partner.id
#             src.opportunity_ids.partner_id = dst_partner.id
#             src.meeting_ids.partner_id = dst_partner.id
#             src.purchase_line_ids.partner_id = dst_partner.id
#             src.sale_order_ids.partner_id = dst_partner.id
#             src.invoice_ids.partner_id = dst_partner.id
#             src.ticket_ids.partner_id = dst_partner.id
#             loyalty_history = self.env['website.loyalty.history'].search([('partner_id', '=', 'src.id')])
#             loyalty_history.partner_id = dst_partner.id
#             dst_partner.write({'parent_id': src.id, 'type': 'invoice'})
