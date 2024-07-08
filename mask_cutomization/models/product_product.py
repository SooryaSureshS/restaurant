from odoo import api, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def create(self, vals):
        result = super(ProductProduct, self).create(vals)
        try:
            result.generate_sku()
        except:
            pass
        return result

    def write(self, vals):
        result = super(ProductProduct, self).write(vals)
        try:
            self.generate_sku()
        except:
            pass
        return result

    def generate_sku(self):
        sku = ''
        if self.is_mask_product:
            try:
                sku += 'K' if self.mask_type == 'korean_style' else 'S' if self.mask_type == 'surgical' else 'F'
                ptv_value_ids = self.product_template_variant_value_ids
                pt = ptv_value_ids.filtered(lambda att: att.attribute_id.name == "Print type")
                sku += pt.product_attribute_value_id.code if pt else ''
                nose = ptv_value_ids.filtered(lambda att: att.attribute_id.name == "Nose sponge")
                sku += nose.product_attribute_value_id.code if nose else ''
                cloth = ptv_value_ids.filtered(lambda att: att.attribute_id.name == "Cloth color")
                sku += cloth.product_attribute_value_id.code if cloth else ''
                loop = ptv_value_ids.filtered(lambda att: att.attribute_id.name == "Earloop color")
                sku += loop.product_attribute_value_id.code if loop else ''
                size = ptv_value_ids.filtered(lambda att: att.attribute_id.name == "Mask size")
                sku += size.product_attribute_value_id.code if size else ''
                # frag = ptv_value_ids.filtered(lambda att: att.attribute_id.name == "Fragrance bead")
                # sku += frag.product_attribute_value_id.code if frag else ''
            except:
                pass
        self.default_code = sku

    def get_qty_price(self, qty):
        website_pricelist = int(
            self.env['ir.config_parameter'].sudo().get_param('mask_cutomization.website_price_list'))
        pricelist = self.env['product.pricelist'].search([('id', '=', int(website_pricelist))], limit=1)
        price = self.lst_price
        if pricelist:
            for item in pricelist.item_ids.search([('id', 'in', pricelist.item_ids.ids)], order="min_quantity"):
                if item.product_id.id == self.id:
                    if item.min_quantity <= float(qty):
                        price = item.fixed_price * float(qty)
        return price
