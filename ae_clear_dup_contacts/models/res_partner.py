# -*- coding: utf-8 -*-
##############################################################################
#    Copyright (C) 2020 AtharvERP (<http://atharverp.com/>). All Rights Reserved
# Odoo Proprietary License v1.0
#
# This software and associated files (the "Software") may only be used (executed,
# modified, executed after modifications) if you have purchased a valid license
# from the authors, typically via Odoo Apps, atharverp.com or you have written agreement from
# author of this software owner.
#
# You may develop Odoo modules that use the Software as a library (typically
# by depending on it, importing it and using its resources), but without copying
# any source code or material from the Software. You may distribute those
# modules under the license of your choice, provided that this license is
# compatible with the terms of the Odoo Proprietary License (For example:
# LGPL, MIT, or proprietary licenses similar to this one).
#
# It is forbidden to publish, distribute, sublicense, or sell copies of the Software
# or modified copies of the Software.
#
# The above copyright notice and this permission notice must be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
##############################################################################

from odoo import models


class ResPartnerExt(models.Model):
    _inherit = 'res.partner'
    _description = 'Partner'

    def clear_duplicates(self):
        duplicate_contacts = []
        user_obj = self.env['res.users']
        cale_obj = self.env['calendar.contacts']
        for partner in self:
            if partner.email and partner not in duplicate_contacts:
                duplicates = self.search([('id', '!=', partner.id), ('email', '=', partner.email)])
                for dup in duplicates:
                    user = user_obj.search([('partner_id', '=', dup.id)])
                    calender = cale_obj.search([('partner_id', '=', dup.id)])
                    if not user and not calender:
                        duplicate_contacts.append(dup)
        print("aseodiuscj", len(duplicate_contacts))

        for i in duplicate_contacts:
            duplicate = i.find(i.id, i.email, duplicate_contacts)
            print("duplicate", duplicate)
            for k in duplicate:
                k.sudo().write({'email': ""})
                if k.sale_order_ids:
                    for sale in k.sale_order_ids:
                        sale.sudo().write({'partner_id': i.id, 'partner_invoice_id': i.id, 'partner_shipping_id': i.id})
                if k.pos_order_ids:
                    for pos in k.pos_order_ids:
                        pos.sudo().write({'partner_id': i.id})
        # for j in duplicate_contacts:
        #     partners = self.env['res.partner'].sudo().search([('id', '=', j.id)])
        #     print("sdsds", partners.id, "  ", partners.name)
        #     partners.unlink()
        print("aslklaskjdaslkdj")

    # def find(self, id, email, duplicate_contacts):
    #     duplicate = []
    #     for x in duplicate_contacts:
    #         if x.id != id and x.email == email:
    #             duplicate.append(x)
    #     return duplicate

    def sale_address_fixes(self):
        sales = self.env['sale.order'].sudo().search([])
        for k in sales:
            if k.partner_id.type != 'contact' and k.partner_id.parent_id:
                k.sudo().write({'partner_id': k.partner_id.parent_id.id})
            if k.partner_id.id != k.partner_invoice_id.id or k.partner_id.id != k.partner_shipping_id.id:
                k.sudo().write({'partner_invoice_id': k.partner_id.id, 'partner_shipping_id': k.partner_id.id})

    def remove_contacts_without_orders(self):

        partners_invoices = self.env['res.partner'].sudo().search(
            [('sale_order_ids', '=', False), ('pos_order_ids', '=', False),
             ('user_ids', '=', False), ('ref_company_ids', '=', False)])
        print("asdsadasd", len(partners_invoices))
        for i in partners_invoices:
            if not i.sale_order_ids and not i.pos_order_ids:
                for inv in i.invoice_ids:
                    inv.button_draft()
                    if i.parent_id:
                        inv.sudo().write({'partner_id': i.parent_id.id, 'partner_shipping_id': i.parent_id.id})
        partners_data = self.env['res.partner'].sudo().search(
            [('sale_order_ids', '=', False), ('pos_order_ids', '=', False), ('invoice_ids', '=', False),
             ('user_ids', '=', False), ('ref_company_ids', '=', False), ('purchase_line_ids', '=', False)])
        print("MMMMMMMMMMM: ", len(partners_data))
        for partner in partners_data:
            print("ASds")
            print(partner.id)
            # try:
            partner.unlink()
            # except:
            #     pass
