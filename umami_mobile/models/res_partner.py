from odoo import models, fields
import logging
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    favourite_product_ids = fields.One2many('favourite.product','partner_id')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ])
    latitude = fields.Char()
    longitude = fields.Char()

    def add_fav_products(self,product_id, partner_id):
        lines = []
        partner = self.env['res.partner'].sudo().search([('id','=',partner_id)])
        product = self.env['product.template'].sudo().search([('id','=',product_id)])
        partner.write({
            'favourite_product_ids': [
                (0,0,{'product_id':product_id})
            ]
        })

    def delete_fav_products(self, product_id,partner_id):
        partner = self.env['res.partner'].sudo().search([('id', '=', partner_id)])
        favourite = self.env['favourite.product'].sudo().search([('product_id', '=', product_id),('partner_id','=',partner_id)])
        partner.sudo().write({
            'favourite_product_ids':[(2, favourite.id)]})
