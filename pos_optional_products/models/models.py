from odoo import models, api, fields, _


class POSOptionalProducts(models.Model):
    _inherit = 'pos.order.line'

    linked_line_id = fields.Many2one('po.order.line', string='Linked Order Line', ondelete='cascade')
    # linked_line_id = fields.Many2one('sale.order.line', string='Linked Order Line', domain="[('order_id', '!=',
    # order_id)]", ondelete='cascade')
    option_line_ids = fields.One2many('pos.order.line', 'linked_line_id', string='Options Linked')


class Products(models.Model):
    _inherit = 'product.product'

    @api.model
    def get_product_id(self, optional_product_ids):

        optional_product = []

        for i in optional_product_ids:
            products = self.env['product.product'].sudo().search([('product_tmpl_id', '=', int(i))], limit=1)
            if products:
                data = {
                    'name': products.name,
                    'id': products.id,
                    'option_group': products.product_tmpl_id.product_option_group,
                    'sequence': products.product_tmpl_id.product_option_group.sequence if products.product_tmpl_id.product_option_group else 0,
                }

                optional_product.append(data)
        return optional_product

    @api.model
    def get_product_full_details(self, optional_product_ids):
        optional_product = []

        for i in optional_product_ids:
            products = self.env['product.product'].sudo().search([('product_tmpl_id', '=', int(i))], limit=1)
            if products:
                data = {
                    'name': products.name,
                    'id': products.id,
                    'option_group': products.product_tmpl_id.product_option_group,
                    'sequence': products.product_tmpl_id.product_option_group.sequence if products.product_tmpl_id.product_option_group else 0,
                }

                optional_product.append(data)
        return optional_product

    @api.model
    def get_bundle_product(self, product):

        print("sasdas", product)
        total_count = 0
        product_id = product
        if product_id:
            product_data = []
            qty_item = []
            product = self.env['product.product'].sudo().search([('id', '=', int(product_id))])
            if product and product.is_bundle_product:
                if product.bundle_product_ids:
                    for pro in product.bundle_product_ids:
                        bundle_prods = []
                        for pros in pro.product_id:
                            optional_product = []
                            groups = pros.optional_product_ids.mapped('product_option_group')
                            for grp in groups:
                                optional_grp = {'optional_product_id': grp.id, 'optional_product_name': grp.name}
                                optional = pros.optional_product_ids.filtered(
                                    lambda r: r.product_option_group.id == grp.id)
                                opt_pro = []
                                for opt in optional:
                                    opti_pro = self.env['product.product'].sudo().search([('product_tmpl_id', '=', opt.id)],
                                                                               limit=1)
                                    opt_pro.append({'product_id': opti_pro.id,
                                                    'product_name': opti_pro.name,
                                                    'price': opt.list_price,
                                                    })

                                optional_grp['products'] = opt_pro
                                optional_product.append(optional_grp)
                            bundle_image_url = '/web/image/product.product/' + str(pro.id) + '/image_128'
                            ch_pro = self.env['product.product'].sudo().search([('product_tmpl_id', '=', pros.id)],
                                                                               limit=1)
                            bundle_prods.append({
                                'choice_product_id': ch_pro.id,
                                'choice_product_name': ch_pro.name,
                                'bundle_extra_price': pros.bundle_extra_price,
                                'optional_product_length': len(optional_product),
                                'optional_product': optional_product,
                                'choice_image_url': bundle_image_url,
                            })
                        total_count = total_count + int(pro.qty)
                        product_data.append({
                            'bundle_product_name': pro.bundle_name,
                            'bundle_product_id': pro.id,
                            'bundle_product_qty': pro.qty,
                            'choice_products': bundle_prods,
                        })
                        qty_item.append(pro.qty)
                    image_url = '/web/image/product.product/' + str(product.id) + '/image_128'
                    vals = {
                        'product': product.id,
                        'image_url': image_url,
                        'add_qty': 1,
                        'bundle_qty': qty_item,
                        'price': product.lst_price,
                        'description': product.description_sale,
                        'parent_name': product.name,
                        'variant_values': product_data,
                        'total_count': total_count
                    }

                    print("OPPO", vals)
                    return vals

                else:
                    return False
            else:
                return False
        else:
            return False

    # @api.model
    # def get_bundle_product(self, product):
    #
    #     print("sasdas", product)
    #     product_id = product
    #     if product_id:
    #         product_data = []
    #         qty_item = []
    #         product = self.env['product.product'].sudo().search([('id', '=', int(product_id))])
    #         print(product.name)
    #         if product and product.is_bundle_product:
    #             if product.bundle_product_ids:
    #
    #                 for pro in product.bundle_product_ids:
    #                     optional_product = []
    #                     groups = pro.product_id.optional_product_ids.mapped('product_option_group')
    #                     for grp in groups:
    #                         optional_grp={'optional_product_id': grp.id,'optional_product_name': grp.name}
    #                         optional=pro.product_id.optional_product_ids.filtered(lambda r:r.product_option_group.id==grp.id)
    #                         opt_pro =[]
    #                         for opt in optional:
    #                             opt_product = self.env['product.product'].sudo().search(
    #                                 [('product_tmpl_id.id', '=', opt.id)])
    #                             print("ooo", opt_product.name, opt_product.available_in_pos)
    #                             if opt_product.available_in_pos:
    #                                 opt_pro.append({'product_id': opt_product.id,
    #                                                 'product_name': opt_product.name,
    #                                                 'price': opt_product.list_price})
    #
    #                         optional_grp['products'] = opt_pro
    #                         optional_product.append(optional_grp)
    #                     par_product = self.env['product.product'].sudo().search(
    #                         [('product_tmpl_id.id', '=', pro.product_id[0].id)], limit=1)
    #                     # print("ooo",par_product.name, par_product.available_in_pos)
    #                     if par_product.available_in_pos:
    #                         product_data.append({'bundle_product_id': par_product.id,
    #                                              'bundle_product_name': par_product.name,
    #                                              'bundle_product_qty': pro.qty,
    #                                              'optional_product': optional_product,
    #                                              'bundle_description': par_product.description_sale,
    #                                              })
    #                     # qty_item.append(pro.qty)
    #                 # chi_product = self.env['product.product'].sudo().search(
    #                 #     [('product_tmpl_id.id', '=', product.id)])
    #                 print("kk", product.name,product.available_in_pos)
    #                 if product.available_in_pos:
    #                     vals = {
    #                         'product': product.id,
    #                         'add_qty': 1,
    #                         'bundle_qty': qty_item,
    #                         'price': product.lst_price,
    #                         'description': product.description_sale,
    #                         'parent_name': product.name,
    #                         'variant_values': product_data,
    #                     }
    #                 print(vals)
    #                 return vals
    #
    #             else:
    #                 return False
    #         else:
    #             return False
    #     else:
    #         return False
