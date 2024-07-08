from odoo import models, fields


class ProdAttrPlWizard(models.TransientModel):
    _name = 'product.attribute.pricelist.wizard'

    ptav_ids = fields.Many2many('product.template.attribute.value', relation='papwptav', string="Attributes")
    pt_id = fields.Many2one('product.template', 'Product')
    pricelist_id = fields.Many2one('product.pricelist')
    quantity = fields.Float()
    price = fields.Float()

    def select(self):
        product_tmpl = self.env['product.template'].browse(self.pt_id.id)
        products = product_tmpl.product_variant_ids.filtered(
            lambda p: all([True if i in p.product_template_variant_value_ids.ids else False for i in self.ptav_ids.ids])
        )
        for product in products:
            price_list_line = self.pricelist_id.item_ids.filtered(lambda i: i.product_id.id == product.id and i.min_quantity == self.quantity)
            if price_list_line:
                price_list_line[0].fixed_price = self.price
            else:
                self.pricelist_id.write({'item_ids': [(0, 0, {
                    'product_tmpl_id': self.pt_id.id,
                    'product_id': product.id,
                    'min_quantity': self.quantity,
                    'fixed_price': self.price
                })]})
            self._cr.commit()
