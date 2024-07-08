# -*- coding: utf-8 -*-
import json
import logging
from datetime import datetime
from werkzeug.exceptions import Forbidden, NotFound

from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.http import request
# from odoo.addons.base.models.ir_qweb_fields import nl2br
# from odoo.addons.http_routing.models.ir_http import slug
# from odoo.addons.payment.controllers.portal import PaymentProcessing
# from odoo.addons.website.controllers.main import QueryURL
# from odoo.addons.website.models.ir_http import sitemap_qs2dom
# from odoo.exceptions import ValidationError
# from odoo.addons.portal.controllers.portal import _build_url_w_params
# from odoo.addons.website.controllers.main import Website
# from odoo.addons.website_form.controllers.main import WebsiteForm
# from odoo.osv import expression
_logger = logging.getLogger(__name__)

class WebsiteGetAccount(http.Controller):

    @http.route('/create/your/mask', website=True, auth='public')
    def create_your_mask(self, page=0, category=None, search='', ppg=False, **post):
        return request.render("mask_cutomization.create_your_mask", {})

class WebsiteSelectMask(http.Controller):

    @http.route('/customize/mask/<model("product.template"):product>', website=True, auth='public')
    def customize_mask(self, product,page=0, category=None, search='', ppg=False, **post):
        sale_order = request.website.sale_get_order(force_create=True)
        if sale_order.state != 'draft':
            request.session['sale_order_id'] = None
            sale_order = request.website.sale_get_order(force_create=True)
        return request.render("mask_cutomization.select_mask_size", {'product': product})


class WebsitePrintArea(http.Controller):

    @http.route(['/print/area/mask/<string:size>/<model("product.template"):product>'], website=True, auth='public')
    def print_area_mask(self,size, product, **post):
        sale_order = request.website.sale_get_order(force_create=True)
        if sale_order:
            if size:
                sale_order.sudo().write({
                    'mask_size': size
                })
        return request.render("mask_cutomization.print_area_mask", {'size': size, 'product': product})

class WebsiteCustomizeDesign(http.Controller):
    def _get_pricelist_context(self):
        pricelist_context = dict(request.env.context)
        pricelist = False
        if not pricelist_context.get('pricelist'):
            pricelist = request.website.get_current_pricelist()
            pricelist_context['pricelist'] = pricelist.id
        else:
            pricelist = request.env['product.pricelist'].browse(pricelist_context['pricelist'])

        return pricelist_context, pricelist

    @http.route(['/mask/designing/<string:area>/<string:size>/<model("product.template"):product>'],website=True, auth='public',type='http')
    def customize_designing(self,  area, size, product, **post):
        sale_order = request.website.sale_get_order(force_create=True)
        session_product_id = False
        session_product_obj = False
        # request.session['session_product_id'] = False
        if request.session.get('session_product_id'):
            session_product_id = request.session.get('session_product_id')
            session_product_obj = request.env['product.line'].sudo().search([('id','=',int(session_product_id))])
            if not session_product_obj:
                pr_lines = request.env['product.line'].sudo().create({
                    "session_product_id": sale_order.id
                })
                sale_order.sudo().write({
                    'upload_your_image': False,
                })
                request.env.cr.commit()
                request.session['session_product_id'] = pr_lines.id
                session_product_id = pr_lines.id
                session_product_obj = pr_lines
            if session_product_obj:
                if not session_product_obj.buffer_image:
                    sale_order.sudo().write({
                        'upload_your_image': False,
                    })

        else:
            sale_order.sudo().write({
                'upload_your_image': False,
            })
            pr_lines = request.env['product.line'].sudo().create({
                "session_product_id": sale_order.id
            })
            request.env.cr.commit()
            request.session['session_product_id'] = pr_lines.id
            session_product_id = pr_lines.id
            session_product_obj = pr_lines
        mask_size = False
        for s_attr in product.valid_product_template_attribute_line_ids:
            if s_attr.attribute_id.name == 'Mask size':
                for s_value in s_attr.product_template_value_ids._only_active():
                    if s_value.name.lower() == size.lower():
                        mask_size = s_value.id
        print_type = False
        for s_attr in product.valid_product_template_attribute_line_ids:
            if s_attr.attribute_id.name == 'Print type':
                for s_value in s_attr.product_template_value_ids._only_active():
                    if s_value.name.lower() == area.lower():
                        print_type = s_value.id
        pricelist = self._get_pricelist_context()
        if sale_order:
            if area:
                sale_order.sudo().write({
                    'mask_area': area,
                    'mask_size': size,
                })

        website_pricelist = int(request.env['ir.config_parameter'].sudo().get_param('mask_cutomization.website_price_list'))
        if website_pricelist:
            sale_order.write({
                'pricelist_id': website_pricelist
            })

        return request.render("mask_cutomization.mask_designing",
                              {'area': area,
                               'sale_order': sale_order,
                               'product': product,
                               'pricelist': pricelist,
                               'mask_size': mask_size,
                               'print_type':print_type,
                               'session_product_id': session_product_id,
                               'session_product_obj': session_product_obj,
                               })

class WebsitePreviewDesign(http.Controller):

    @http.route('/mask/preview/<model("product.product"):product>/<string:line>', website=True, auth='user')
    def mask_preview(self, product,line, **post):
        sale_order = request.website.sale_get_order(force_create=True)
        if product:
            return request.render("mask_cutomization.mask_preview",
                                  {'product': product, 'line': line, 'order': sale_order.id})

    @http.route('/mask/load/<model("product.product"):product>/<model("sale.order.line"):line>/<string:position>', type="http", website=True, auth='public')
    def mask_preview1(self, product, line, position, **post):
        rop_color = False
        mask_color = False
        image = False
        lines = request.env['sale.order.line'].sudo().search([('id', '=', int(line))], limit=1)
        if lines:
            image = line.order_id.id
        for i in product.product_template_attribute_value_ids:
            if i.attribute_id.name == 'Color':
                rop_color = i.html_color
            if i.attribute_id.name == 'Mask color':
                mask_color = i.html_color
            _logger.info('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ %s', i)
            _logger.info('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ %s', i.attribute_id.name)
            # _logger.info('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ %s', i.attribute_id)
            _logger.info('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ %s', i.html_color)
            _logger.info('****************************************** %s', i.product_attribute_value_id.html_color)
        _logger.info('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ %s', rop_color)
        _logger.info('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ %s', mask_color)
        return request.render("mask_cutomization.mask_load", {
            'product': product,
            'rop_color': rop_color,
            'mask_color': mask_color,
            'image': image,
            'position': position,
            'area': lines.order_id.mask_area,
            'line_id': lines.id,
            'bg_image': lines.upload_your_image})

    @http.route('/mask/design/load/<model("product.product"):product>/<model("sale.order"):order>/<string:position>',
                type="http", website=True, auth='public')
    def mask_design_preview1(self, product, order, position, **post):
        rop_color = False
        mask_color = False
        image = False
        # lines = request.env['sale.order'].sudo().search([('id','=',int(order))], limit=1)
        if order:
            image = order.id
        for i in product.product_template_attribute_value_ids:
            if i.attribute_id.name == 'Earloop color':
                rop_color = i.html_color
            if i.attribute_id.name == 'Cloth color':
                mask_color = i.html_color
        # attributes = dict()
        # for ptav in product.product_template_variant_value_ids:
        #     attributes[ptav.attribute_id.name] = ptav.id


        return request.render("mask_cutomization.mask_design_load", {
            'product': product,
            'rop_color': rop_color,
            'mask_color': mask_color,
            'image': image,
            'position': position,
            'area': order.mask_area,
            'order': order.id,
            'bg_image': order.upload_your_image,
            # 'attributes': attributes,

        })


    @http.route('/mask/packaging/<model("product.product"):product>/<model("product.line"):line>', type="http", website=True, auth='public')
    def mask_packaging(self,product,line,  **post):

        return request.render("mask_cutomization.mask_packaging", {'product': product, 'line': line})

    @http.route('/submit/package', type="http", website=True, auth='public')
    def submit_packaging(self, **kw):
        sale_order_line = kw.get('sale_order_line', False)
        product_info = kw.get('product_info', False)
        url = "/carton/packaging/" + str(product_info) + "/" + str(sale_order_line)
        return request.redirect(url, 303)

    @http.route('/submit/carton', type="http", website=True, auth='public')
    def submit_packaging_carton(self, **kw):
        # packaging = False
        sale_order = request.website.sale_get_order(force_create=True)
        session_id = kw.get('sale_order_line', False)
        product_info = kw.get('product_info', False)
        if session_id:
            session_line = request.env['product.line'].sudo().search([('id', '=', int(session_id))], limit=1)
            if session_line and sale_order:
                values = {
                    'order_id': sale_order.id,
                    'customer_lead': 1,
                    'product_id': session_line.product_id.id or False,
                    'product_uom_qty': int(session_line.qty) or 0,
                    'upload_your_image': session_line.buffer_image or False,
                    'upload_file_name': session_line.buffer_image_name or False,
                    'packaging_image': session_line.packaging_image or False,
                    'package_upload_file_name': session_line.packaging_image_name or False,
                    'carton_packaging_image': session_line.carton_packaging_image or False,
                    'carton_upload_file_name': session_line.carton_upload_file_name or False,
                    'mask_size': sale_order.mask_size or False,
                    'mask_area': sale_order.mask_area or False,
                    'with_nose_pad': session_line.is_nosepad,
                    'price_nose_pad': session_line.price_nose_pad
                }
                order_line = request.env['sale.order.line'].sudo().create(values)
                if order_line:
                    product = request.env['product.product'].sudo().search([('id', '=', int(product_info))], limit=1)
                    val = {
                        'name': "Package_" + str(order_line.product_id.name) + "_" + str(sale_order.name),
                        'product_id': order_line.product_id.id,
                        'qty': order_line.product_uom_qty or False,
                        'package_image': order_line.packaging_image or False,
                        'carton_image': order_line.carton_packaging_image or False,
                        'carton_package': True,
                    }
                    packaging = request.env['product.packaging'].sudo().create(val)
                    if packaging:
                        order_line.sudo().write({
                            'product_packaging_id': packaging.id
                        })
                url = "/shop/cart"
                request.session['session_product_id'] = False
                return request.redirect(url, 303)
        else:
            return False


    @http.route('/carton/packaging/<model("product.product"):product>/<model("product.line"):line>', type="http", website=True, auth='public')
    def carton_packaging(self,product,line,  **post):
        if request.session.get('session_product_id'):
            return request.render("mask_cutomization.carton_packaging", {'product': product, 'line': line})
        else:
            return request.redirect("/", 303)
import cgi
from odoo.exceptions import UserError, ValidationError
from odoo.addons.website.controllers.main import Website
class Sunxia(http.Controller):
    @http.route('/upload', type="http", auth="public", methods=['GET', 'POST'], website=True, )
    def upload_file3(self, **kw):
        sale_order = request.website.sale_get_order(force_create=True)
        if sale_order:
            import base64
            file = kw.get('uploaded', False)
            file1 = kw.get('uploaded', False).stream.read()
            sale_order.sudo().write({
                'upload_your_image': base64.encodestring(file1),
                'upload_file_name': kw.get('uploaded', False).filename
            })
        return

    @http.route('/package/logo', type="http", auth="public", methods=['GET', 'POST'], website=True, )
    def upload_file1(self, **kw):
        import base64
        line = kw.get('line', False)
        if line:
            sale_order_line = request.env['sale.order.line'].sudo().search([('id', '=', int(line))], limit=1)
            file1 = kw.get('uploaded', False).stream.read()
            sale_order_line.sudo().write({
                'packaging_image': base64.encodestring(file1),
                'upload_file_name': kw.get('uploaded', False).filename
            })
        return

    @http.route('/carton/logo', type="http", auth="public", methods=['GET', 'POST'], website=True, )
    def upload_file(self, **kw):
        import base64
        line = kw.get('line', False)
        if line:
            sale_order_line = request.env['sale.order.line'].sudo().search([('id', '=', int(line))], limit=1)
            file1 = kw.get('uploaded', False).stream.read()
            sale_order_line.sudo().write({
                'carton_packaging_image': base64.encodestring(file1),
                'carton_upload_file_name': kw.get('uploaded', False).filename
            })
        return

    @http.route(['/product/attribute/search'], type='json', auth="public", methods=['POST'], website=True)
    def product_search_attribute(self, sale_order=None, color_variant=None, product_temp=None, mask_variant=None, **kw):
        if product_temp:
            product_template = request.env['product.template'].search([('id', '=', int(product_temp))], limit=1)
        else:
            product_template = request.env['product.template'].search([('id', '=', int(kw.get('product')))], limit=1)
        sale_order = request.website.sale_get_order(force_create=True)
        mask_attr = False
        product = False
        if mask_variant:
            if color_variant:
                mask_list = []
                mask_list.append(color_variant)
                mask_list.append(mask_variant)
                for i in product_template.product_variant_ids:
                    y = False
                    z = False
                    for k in i.product_template_variant_value_ids:
                        if k.attribute_id.name == 'Color' and color_variant:
                            if k.id == int(color_variant):
                                y = True
                        if k.attribute_id.name == 'Mask color' and mask_variant:
                            if k.id == int(mask_variant):
                                z = True
                    if y and z:
                        product = i.id
        else:
            if mask_attr and color_variant:
                mask_list = []
                mask_list.append(mask_attr)
                mask_list.append(color_variant)
                for i in product_template.product_variant_ids:
                    x = False
                    y = False
                    z = False
                    for k in i.product_template_variant_value_ids:
                        if k.attribute_id.name == 'gender size':
                            if k.id == int(mask_attr):
                                x = True
                        if k.attribute_id.name == 'Color':
                            if k.id == int(color_variant):
                                y = True
                    if x and y:
                        product = i.id
        return product

    @http.route('/submit/product/cart', type="http", auth="public", methods=['GET', 'POST'], website=True, )
    def submitPost(self, **kw):
        sale_order = request.website.sale_get_order(force_create=True)
        sale_order_line = False
        website_pricelist = int(
            request.env['ir.config_parameter'].sudo().get_param('mask_cutomization.website_price_list'))
        if website_pricelist:
            sale_order.write({
                'pricelist_id': website_pricelist
            })
        if sale_order:
            if kw.get('product_varients') != 'None':
                sale_order_line = request.env['sale.order.line'].sudo().create({
                    'order_id': sale_order.id,
                    'customer_lead': 1,
                    'product_id': int(kw.get('product_varients')),
                    'product_uom_qty': int(kw.get('product_qty')) or 0,
                    'upload_your_image': sale_order.upload_your_image or False,
                    'upload_file_name': sale_order.upload_file_name or False,
                    'mask_size': sale_order.mask_size or False,
                    'mask_area': sale_order.mask_area or False,
                })
                if sale_order_line:
                    # sale_order_line.compute_upload_your_image()
                    if sale_order:
                        sale_order.sudo().write({
                            'upload_your_image': False,
                            'upload_file_name': False,
                        })
            else:
                return False


            if kw.get('product_charges') != 'None':
                if request.website._website_service_product():
                    request.env['sale.order.line'].sudo().create({
                        'order_id': sale_order.id,
                        'customer_lead': 1,
                        'product_id': int(request.website._website_service_product().id),
                        'product_uom_qty': int(kw.get('product_qty')) or 0,
                        'linked_line_id': sale_order_line.id or False
                    })
            if kw.get('product_varients') != 'None':
                # url = "/mask/preview/"+str(kw.get('product_varients'))+"/"+str(sale_order_line.id)
                url = "/mask/packaging/" + str(kw.get('product_varients')) + "/" + str(sale_order_line.id)
                # window.location.href = '/mask/packaging/' + product + '/' + line + '/'
                return request.redirect(url)

    @http.route(['/product/preview/info'], type='json', auth="public", methods=['POST'], website=True)
    def productPreviewInfo(self, **kw):
        sale_order = request.website.sale_get_order(force_create=True)
        dict = {}
        lists = []
        band_color = False
        product_name = False
        if sale_order:
            for line in sale_order.order_line:
                if line.product_id.is_mask_product:
                    product_name = line.product_id.name
                    for k in line.product_id.product_template_variant_value_ids:
                        if k.attribute_id.name == 'Color':
                            band_color = k.html_color
            dict = {
                # 'uploaded_image': var url = window.location.origin+'/web/image?model=sale.order&id='+sale_order+'&field=kit_personalisation_image
                "order_id": sale_order.id,
                "product_color": band_color,
                "product_name": product_name,
                "image": sale_order.upload_your_image or False
            }
            return dict
        else:
            return False


    @http.route(['/amount/fetch'], type='json', auth="public", methods=['POST'], website=True)
    def product_amount_fetch(self, product_variants=None, nose_pad=None, qty=None, is_nosepad=None, **kw):
        amount = 0
        amount1 = 0
        if product_variants:
            if product_variants != 'None':
                product = request.env['product.product'].search([('id', '=', int(product_variants))], limit=1)
                website_pricelist = int(
                    request.env['ir.config_parameter'].sudo().get_param('mask_cutomization.website_price_list'))
                pricelist = request.env['product.pricelist'].search([('id', '=', int(website_pricelist))], limit=1)
                price = product.lst_price
                if pricelist:
                    for item in pricelist.item_ids.search([('id', 'in', pricelist.item_ids.ids)], order="min_quantity"):
                        if item.product_id.id == product.id:
                            if item.min_quantity <= float(qty):
                                price = item.fixed_price
                else:
                    price = product.lst_price
                amount = float(price) * float(qty)
        if nose_pad != 'false':
            if nose_pad != 'None':
                product_id = int(request.env['ir.config_parameter'].sudo().get_param('mask_cutomization.nose_product'))
                product1 = request.env['product.template'].search([('id', '=', int(product_id))], limit=1)

                website_pricelist = int(
                    request.env['ir.config_parameter'].sudo().get_param('mask_cutomization.website_price_list'))
                pricelist = request.env['product.pricelist'].search([('id', '=', int(website_pricelist))], limit=1)
                price1 = product1.list_price
                if pricelist:
                    for item in pricelist.item_ids.search([('id', 'in', pricelist.item_ids.ids)], order="min_quantity"):
                        if item.product_id.id == product1.id:
                            if item.min_quantity <= float(qty):
                                price1 = item.fixed_price
                else:
                    price1 = product1.list_price
                amount1 = float(price1) * float(qty)
                amount = amount + amount1
        return amount

class WebsiteHomeInherit(Website):

    @http.route('/', type='http', auth="public", website=True, sitemap=True)
    def index(self, **kw):
        top_menu = request.website.menu_id

        homepage = request.website.homepage_id
        if homepage and (
                homepage.sudo().is_visible or request.env.user.has_group('base.group_user')) and homepage.url != '/':
            return request.env['ir.http'].reroute(homepage.url)

        website_page = request.env['ir.http']._serve_page()
        if website_page:
            return website_page

        else:
            first_menu = top_menu and top_menu.child_id and top_menu.child_id.filtered(lambda menu: menu.is_visible)
            if first_menu and first_menu[0].url not in ('/', '', '#') and (
            not (first_menu[0].url.startswith(('/?', '/#', ' ')))):
                return request.redirect(first_menu[0].url)

        raise request.not_found()

    @http.route('/product/shop/<model("product.template"):product>', type='http', auth="public", website=True, sitemap=True)
    def productDetails(self, product, **kw):
        if product:
            return request.render("mask_cutomization.product_details", {'product': product})


    @http.route(['/product/details'], type='json', auth="public", methods=['POST'], website=True)
    def product_search_attribute_details(self, line, product, **kw):
        rop_color = False
        mask_color = False
        if product:
            product_info = request.env['product.product'].search([('id', '=', int(product))], limit=1)
            for i in product_info.product_template_attribute_value_ids:
                if i.attribute_id.name == 'Color':
                    rop_color = i.html_color
                if i.attribute_id.name == 'Mask color':
                    mask_color = i.html_color
        return {
            'mask_color': mask_color,
            'rop_color': rop_color,
        }

    @http.route(['/shop/cart/qty/update'], type='json', auth="public", methods=['POST'], website=True)
    def shop_product_qty_update(self, line, qty, **kw):
        if line and qty:
            product_info = request.env['sale.order.line'].sudo().search([('id', '=', int(line))], limit=1)
            if product_info:
                product_info.sudo().write({
                    'product_uom_qty': qty
                })
                if product_info.option_line_ids:
                    for options in product_info.option_line_ids:
                        options.sudo().write({
                            'product_uom_qty': qty
                        })

                if float(qty) <= 0:
                    if product_info.option_line_ids:
                        for options in product_info.option_line_ids:
                            options.sudo().unlink()
                    product_info.sudo().unlink()
                return True

    @http.route(['/website/mask/object'], type='json', auth="public", methods=['POST'], website=True)
    def website_mask_objects(self, product_id, **kw):
        product = request.env['product.template'].sudo().search([('id', '=', product_id)], limit=1)
        if product:
            info = {
                'product': product.id or False,
                'main_mask_material_name': product.main_mask_material_name or False,
                'nose_pad_material_name': product.nose_pad_material_name or False,
                'ear_rope_material_name': product.ear_rope_material_name or False,
                'logo_material_name': product.logo_material_name or False,
                'logo_material_name2': product.logo_material_name2 or False,
                'logo_material_name3': product.logo_material_name3 or False,
                'logo_material_name4': product.logo_material_name4 or False,
                'jaw_pad': product.jaw_pad or False,
                'main_mask_back': product.main_mask_back or False,
                'main_mask_front': product.main_mask_front or False,
                'root_inspection': product.root_inspection or False,
                'pointed_light': product.pointed_light or False,
                'mask_position_x': product.mask_position_x,
                'mask_position_y': product.mask_position_y,
                'mask_position_z': product.mask_position_z,
                'mask_rotation': product.mask_rotation or False,
                'ambient_light': product.ambient_light or False,
                'background_color': product.background_color or False,
                'repeat_x': product.repeat_x or False,
                'repeat_y': product.repeat_y or False,
                'gltf_background_image': product.gltf_background_image or False,
                'parent_logo': product.parent_logo or False,
            }
            return info
        else:
            return False

    @http.route(['/package/image/delete'], type='json', auth="public", methods=['POST'], website=True)
    def package_image_delete(self, line, **kw):
        if line:
            s_line = request.env['product.line'].sudo().search([('id', '=', int(line))], limit=1)
            if s_line:
                s_line.sudo().write({
                    'packaging_image': False,
                    'packaging_image_name': False
                })
                return True
        return False

    @http.route(['/carton/image/delete'], type='json', auth="public", methods=['POST'], website=True)
    def carton_image_delete(self, line, **kw):
        if line:
            s_line = request.env['product.line'].sudo().search([('id', '=', int(line))], limit=1)
            if s_line:
                s_line.sudo().write({
                    'carton_packaging_image': False,
                    'carton_upload_file_name': False
                })
                return True
        return False

    @http.route('/image/editor/<model("product.template"):product>', type='http', auth="public", website=True,sitemap=True)
    def image_editor(self,product,**kw):
        sale_order = request.website.sale_get_order(force_create=True)
        session_product_id = request.session.get('session_product_id')
        if sale_order and session_product_id:
            return request.render("mask_cutomization.mask_image_editor", {"product": product, "order": sale_order, "session_product_id": session_product_id})


    @http.route(['/image/save/editor'], type='json', auth="public", methods=['POST'], website=True)
    def image_editor_save(self, image, name, **kw):
        sale_order = request.website.sale_get_order(force_create=True)
        # request.session['sessio'] = order.id
        if sale_order:
            if not request.session.get('session_product_id'):
                session_product_id = request.env['product.line'].sudo().create({
                    'session_product_id': sale_order.id,
                    'buffer_image': image,
                    'buffer_image_name': name,
                })
                sale_order.write({
                    "upload_your_image": image
                })
                request.session['session_product_id'] = session_product_id.id
            else:
                session_product_id = request.session.get('session_product_id')
                session_product_obj = request.env['product.line'].sudo().search([('id', '=', int(session_product_id))])
                session_product_obj.sudo().write({
                    'session_product_id': sale_order.id,
                    'buffer_image': image,
                    'buffer_image_name': name,
                })
                sale_order.write({
                    "upload_your_image": image
                })
            return True
        else:
            return False

    @http.route(['/image/details/editor'], type='json', auth="public", methods=['POST'], website=True)
    def image_editor_details(self, product_id, **kw):
        if product_id:
            product_id_info = request.env['product.template'].sudo().search([('id', '=', int(product_id))])
            if product_id_info:
                dict = {
                    'preview_full_area': product_id_info.preview_full_area,
                    'preview_logo_area': product_id_info.preview_logo_area,
                }
                return dict
        else:
            return False

    @http.route(['/get/crop/image/details'], type='json', auth="public", methods=['POST'], website=True)
    def get_editor_image_details_info(self, product_id, **kw):
        if product_id:
            pro = request.env['product.template'].sudo().search([('id','=',int(product_id))])
            dict = {
                'preview_full_area': pro.preview_full_area,
                'preview_logo_area': pro.preview_logo_area,
                'logo_crop_width': pro.logo_crop_width,
                'logo_crop_height': pro.logo_crop_height,
                'full_crop_width': pro.full_crop_width,
                'full_crop_height': pro.full_crop_height,
            }
            return dict
        else:
            return False

from odoo.addons.website_sale.controllers.main import WebsiteSale
class WebsiteSaleMskCustomization(WebsiteSale):


    def checkout_values(self, **kw):
        values = {}
        values = super(WebsiteSaleMskCustomization, self).checkout_values(**kw)
        order = request.website.sale_get_order()
        values['shipping_address'] = False
        if values['shippings']:
            for i in values['shippings']:
                order.partner_shipping_id == i
                values['shipping_address'] = order.partner_shipping_id
        return values

    @http.route()
    def shop(self, page=0, category=None, search='', min_price=0.0, max_price=0.0, ppg=False, **post):
        return request.redirect('/')

    @http.route(['/product/size/fetch'], type='json', auth="public", methods=['POST'], website=True)
    def product_size_fetch(self, product, **kw):
        product_info = request.env['product.template'].sudo().search([('id', '=', int(product))], limit=1)
        if product_info:
            dict = {
                'logo_crop_width': product_info.logo_crop_width,
                'logo_crop_height': product_info.logo_crop_height,
            }
            return dict
        else:
            return False

    @http.route()
    def cart(self, access_token=None, revive='', **post):
        values = super(WebsiteSaleMskCustomization, self).cart(**post)
        return values

    @http.route('/package/logo/write', type="json", auth="public", methods=['POST'], website=True)
    def upload_file_write(self, image, name, line, **kw):
        order = request.website.sale_get_order()
        if order:
            sale_order_line = request.env['product.line'].sudo().search([('id', '=', int(line))], limit=1)
            sale_order_line.sudo().write({
                'packaging_image': image,
                'packaging_image_name': name
            })
            return True
        else:
            return False

    @http.route('/carton/logo/write', type="json", auth="public", methods=['POST'], website=True)
    def upload_carton_file_write(self, image, name, line, **kw):
        order = request.website.sale_get_order()
        if order:
            sale_order_line = request.env['product.line'].sudo().search([('id', '=', int(line))], limit=1)
            sale_order_line.sudo().write({
                'carton_packaging_image': image,
                'carton_upload_file_name': name
            })
            return sale_order_line.id
        else:
            return False

    @http.route('/package/history', type="json", auth="public", methods=['POST'], website=True)
    def upload_history_write(self, line, **kw):
        line = request.env['product.line'].search([('id', '=', int(line))], limit=1)
        order = request.env['sale.order'].search([('id', '=', int(line.session_product_id))], limit=1)
        if line:
            url = '/mask/designing/' + str(order.mask_area) + '/' + str(order.mask_size) + '/' + str(
                line.product_id.product_tmpl_id.id)
            # line.unlink()
            return url
        return False

    @http.route('/product/variant/search', type="json", auth="public", methods=['GET', 'POST'], csrf=False)
    def product_variant_search(self):
        try:
            url = request.httprequest.host_url
            data = request.httprequest.data
            data = json.loads(data)
            if data['params']:
                data = data['params']
            product_tmpl_id = data.get('product_tmpl_id')
            attributes = data.get('attributes')
            if not attributes:
                return {
                    'status': 0,
                    'message': 'Missing product attributes'
                }
            print_type = attributes.get('print_type')
            nose_sponge = attributes.get('nose_sponge')
            cloth_color = attributes.get('cloth_color')
            earloop_color = attributes.get('earloop_color')
            mask_size = attributes.get('mask_size')
            # fragrance = attributes.get('fragrance')
            if print_type and nose_sponge and cloth_color and earloop_color and mask_size:
                products = request.env['product.product'].sudo().search(
                    [('product_tmpl_id.id', '=', int(product_tmpl_id))]).filtered(
                    lambda p: int(print_type) in p.product_template_variant_value_ids.ids
                              and int(nose_sponge) in p.product_template_variant_value_ids.ids
                              and int(cloth_color) in p.product_template_variant_value_ids.ids
                              and int(earloop_color) in p.product_template_variant_value_ids.ids
                              and int(mask_size) in p.product_template_variant_value_ids.ids

                )

                return {
                    'status': 1,
                    'product': products[0].id
                }
            else:
                return {
                    'status': 0,
                    'message': 'Missing product attribute %s' % (
                        'print_type' if not print_type else 'nose_sponge' if not nose_sponge else 'cloth_color' if not cloth_color else 'earloop_color' if not earloop_color else 'mask_size' if not mask_size else 'fragrance')
                }
        except Exception as e:
            return {
                'status': 0,
                'message': e
            }

    @http.route('/submit/product/session/cart', type="http", auth="public", methods=['GET', 'POST'], website=True, )
    def SumbmitSessionPost(self, **kw):
        sale_order = request.website.sale_get_order(force_create=True)
        website_pricelist = int(
            request.env['ir.config_parameter'].sudo().get_param('mask_cutomization.website_price_list'))
        if website_pricelist:
            sale_order.write({
                'pricelist_id': website_pricelist
            })
        if kw.get('session_product_id'):
            product_line = request.env['product.line'].sudo().search([('id', '=', int(kw.get('session_product_id')))],
                                                                     limit=1)
            if kw.get('product_varients'):
                product_line.sudo().write({
                    'product_id': int(kw.get('product_varients')),
                    'qty': int(kw.get('product_qty')),
                    'is_nosepad': kw.get('is_nosepad'),
                    'price_nose_pad': float(kw.get('nose_pad_price'))
                })

            if kw.get('product_varients') != 'None':
                url = "/mask/packaging/" + str(kw.get('product_varients')) + "/" + str(kw.get('session_product_id'))
                return request.redirect(url)

    @http.route(['/search/fields'], type='json', auth="public", methods=['POST'], website=True)
    def search_fields(self, id=None, model=None, field=None, **kw):
        if id:
            info = request.env[model].search_read([('id', '=', int(id))], limit=1)
            if info:
                return info[0]

    @http.route('/product/ptav/get', type="json", auth="public", methods=['GET', 'POST'], csrf=False)
    def product_ptav(self, pid=None):
        try:
            product = request.env['product.product'].sudo().browse(int(pid))
            attributes = dict()
            for ptav in product.product_template_variant_value_ids:
                attributes[ptav.attribute_id.name] = ptav.id
            return {
                'status': 1,
                'pid': pid,
                'attributes': attributes
            }
        except Exception as e:
            return {
                'status': 0,
                'message': e
            }
    @http.route('/about_us', type='http', auth="public", website=True, sitemap=True)
    def aboutDetails(self, **kw):
        return request.render("mask_cutomization.about_us")

    @http.route('/contact_us', type='http', auth="public", website=True, sitemap=True)
    def ContactUsDetails(self, **kw):
        return request.render("mask_cutomization.contact_us")

    @http.route('/contact_us/success', type='http', auth="public", website=True, sitemap=True)
    def ContactSucessUsDetails(self, **kw):
        return request.render("mask_cutomization.contactus_success")


    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def address(self, **kw):
        order = request.website.sale_get_order()
        Partner = request.env['res.partner'].with_context(show_address=1).sudo()
        new = False
        edit = False
        mode = False
        values = {}
        partner_id = Partner
        # if 'submitted' in kw and request.httprequest.method == "POST":
        invoice_partner_id = False
        partner_shipping_id = False
        if kw.get('partner_id'):
            edit = True
        if kw.get('type') == 'edit_billing' and edit:
            mode = 'billing'
            if kw.get('partner_id'):
                invoice_partner_id = request.env['res.partner'].sudo().search([('id','=',int(kw.get('partner_id')))], limit=1)
        if kw.get('type') == 'edit_shipping' and edit:
            mode = 'shipping'
            if kw.get('partner_id'):
                partner_shipping_id = request.env['res.partner'].sudo().search([('id', '=', int(kw.get('partner_id')))],
                                                                              limit=1)

        countries = request.env['res.country'].sudo().search([])
        country_states = request.env['res.country.state'].sudo().search([])
        if not mode:
            mode = 'new'
        if not partner_id:
            partner_id = order.partner_id
        render_values = {
            'website_sale_order': order,
            'partner_id': partner_id,
            'mode': mode,
            'invoice_address': invoice_partner_id,
            'delivery_address': partner_shipping_id,
            'countries': countries,
            'country_states': country_states,
            'delivery': kw.get('delivery') or False,
            # 'checkout': values,
            # 'can_edit_vat': can_edit_vat,
            # 'error': errors,
            # 'callback': kw.get('callback'),
            # 'only_services': order and order.only_services,
        }
        print("render values",render_values)
        return request.render("website_sale.address", render_values)


    @http.route(['/save/address'], type='http', methods=['GET', 'POST'], auth="public", website=True,sitemap=False)
    def editSaveAddress(self, **kw):
        order = request.website.sale_get_order()
        Partner = request.env['res.partner'].with_context(show_address=1).sudo()
        if not kw.get('delivery'):
            if kw.get('mode') == 'new' or kw.get('mode') == 'billing':
                value_dict = {
                    'name': kw.get('b_name') or False,
                    'street': kw.get('b_street') or False,
                    'street2': kw.get('b_street2') or False,
                    'city': kw.get('b_city') or False,
                    'state_id': kw.get('b_state_id') or False,
                    'country_id': int(kw.get('b_country_id')) or False,
                    'zip': kw.get('b_zip') or False,
                    'email': kw.get('b_email') or False,
                    'phone_code': kw.get('b_phone_code') or False,
                    'phone': kw.get('b_phone') or False,
                    'company_name': kw.get('b_company_name') or False,
                }
                if kw.get('invoice_partner_id') and not request.website.is_public_user():
                    p_obj = Partner.sudo().search([('id','=',int(kw.get('invoice_partner_id')))],limit=1)
                    if p_obj:
                        a = p_obj.sudo().write(value_dict)
                        order.partner_invoice_id = p_obj.id
                        request.env.cr.commit()
                else:
                    value_dict = {
                        'name': kw.get('b_name') or False,
                        'street': kw.get('b_street') or False,
                        'street2': kw.get('b_street2') or False,
                        'city': kw.get('b_city') or False,
                        'state_id': kw.get('b_state_id') or False,
                        'country_id': int(kw.get('b_country_id')) or False,
                        'zip': kw.get('b_zip') or False,
                        'email': kw.get('b_email') or False,
                        'phone_code': kw.get('b_phone_code') or False,
                        'phone': kw.get('b_phone') or False,
                        'company_name': kw.get('b_company_name') or False,
                        'type': 'invoice',
                    }
                    a = Partner.sudo().create(value_dict)
                    order.partner_invoice_id = a.id
                    order.partner_id = a.id
                    request.env.cr.commit()


                if kw.get('appy_billing') == 'on':
                    # delivery address mappping
                    value_dict2 = {
                        'name': kw.get('name') or False,
                        'street': kw.get('street') or False,
                        'street2': kw.get('street2') or False,
                        'city': kw.get('city') or False,
                        'state_id': kw.get('state_id') or False,
                        'country_id': int(kw.get('country_id')) or False,
                        'zip': kw.get('zip') or False,
                        'email': kw.get('email') or False,
                        'phone_code': kw.get('phone_code') or False,
                        'phone': kw.get('phone') or False,
                        'company_name': kw.get('company_name') or False,
                        'parent_id': order.partner_id.id or False,
                        'type': 'delivery',
                    }
                    p_obj = Partner.sudo().create(value_dict2)
                    order.partner_shipping_id = p_obj.id
                    request.env.cr.commit()
            else:
                value_dict2 = {
                    'name': kw.get('name') or False,
                    'street': kw.get('street') or False,
                    'street2': kw.get('street2') or False,
                    'city': kw.get('city') or False,
                    'state_id': kw.get('state_id') or False,
                    'country_id': int(kw.get('country_id')) or False,
                    'zip': kw.get('zip') or False,
                    'email': kw.get('email') or False,
                    'phone_code': kw.get('phone_code') or False,
                    'phone': kw.get('phone') or False,
                    'company_name': kw.get('company_name') or False,
                    # 'parent_id': order.partner_id.id or False,
                    'type': 'delivery',
                }
                if kw.get('delivery_address_id'):
                    p_obj = Partner.sudo().search([('id','=',int(kw.get('delivery_address_id')))],limit=1)

                    s=p_obj.sudo().write(value_dict2)
                    order.partner_shipping_id = p_obj.id
                    request.env.cr.commit()
                # return request.redirect('/shop/address')
        else:
            value_dict2 = {
                'name': kw.get('name') or False,
                'street': kw.get('street') or False,
                'street2': kw.get('street2') or False,
                'city': kw.get('city') or False,
                'state_id': kw.get('state_id') or False,
                'country_id': int(kw.get('country_id')) or False,
                'zip': kw.get('zip') or False,
                'email': kw.get('email') or False,
                'phone_code': kw.get('phone_code') or False,
                'phone': kw.get('phone') or False,
                'company_name': kw.get('company_name') or False,
                'parent_id': order.partner_id.id or False,
                'type': 'delivery',
            }
            p_obj = Partner.sudo().create(value_dict2)
            order.partner_shipping_id = p_obj.id
            request.env.cr.commit()
        return request.redirect('/shop/checkout')



    @http.route(['/shop/checkout'], type='http', auth="public", website=True, sitemap=False)
    def checkout(self, **post):
        order = request.website.sale_get_order()
        redirection = self.checkout_redirection(order)
        if order.partner_invoice_id.id == 4:
            return request.redirect('/shop/address')
        if order.partner_id != order.partner_shipping_id.parent_id:
            return request.redirect('/shop/address?delivery=True')
        # if not order.partner_shipping_id:
        if redirection:
            return redirection

        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            return request.redirect('/shop/address')

        redirection = self.checkout_check_address(order)
        if redirection:
            return redirection

        values = self.checkout_values(**post)
        if post.get('express'):
            return request.redirect('/shop/confirm_order')

        values.update({'website_sale_order': order})

        # Avoid useless rendering if called in ajax
        if post.get('xhr'):
            return 'ok'
        return request.render("website_sale.checkout", values)

from odoo.addons.portal.controllers.web import Home
class WebsiteSaleMskCustomizations(Home):

    def _login_redirect(self, uid, redirect=None):
        if not redirect and not request.env['res.users'].sudo().browse(uid).has_group('base.group_user'):
            redirect = '/'
        return super(Home, self)._login_redirect(uid, redirect=redirect)

from odoo.addons.auth_signup.controllers.main import AuthSignupHome
import werkzeug
from odoo.addons.auth_signup.models.res_users import SignupError
class WebsiteSaleMskCustomizationsAuth(AuthSignupHome):

    def _prepare_signup_values(self, qcontext):
        values = {key: qcontext.get(key) for key in ('login', 'name', 'password', 'phone', 'phone_code')}
        if not values:
            raise UserError(_("The form was not properly filled in."))
        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords do not match; please retype them."))
        supported_lang_codes = [code for code, _ in request.env['res.lang'].get_installed()]
        lang = request.context.get('lang', '')
        if lang in supported_lang_codes:
            values['lang'] = lang
        return values

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                try:
                    qcontext.update({
                        'phone': kw.get('phone')
                    })
                    qcontext.update({
                        'phone_code': kw.get('phone_code')
                    })
                except:
                    pass
                self.do_signup(qcontext)
                # Send an account creation confirmation email
                if qcontext.get('token'):
                    User = request.env['res.users']
                    user_sudo = User.sudo().search(
                        User._get_login_domain(qcontext.get('login')), order=User._get_login_order(), limit=1
                    )
                    template = request.env.ref('auth_signup.mail_template_user_signup_account_created',
                                               raise_if_not_found=False)
                    if user_sudo and template:
                        template.sudo().send_mail(user_sudo.id, force_send=True)
                return self.web_login(*args, **kw)
            except UserError as e:
                qcontext['error'] = e.args[0]
            except (SignupError, AssertionError) as e:
                if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                    qcontext["error"] = _("Another user is already registered using this email address.")
                else:
                    _logger.error("%s", e)
                    qcontext['error'] = _("Could not create a new account.")

        response = request.render('auth_signup.signup', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

from odoo.addons.website_sale.controllers import main
class WebsiteSaleInherit(main.WebsiteSale):
    @http.route(['/shop/cart'], type='http', auth="public", website=True)
    def cart(self, **post):
        order = request.website.sale_get_order()
        # order.recompute_coupon_lines()
        order.sudo().write({
            'upload_your_image': False,
        })

        return super(WebsiteSaleInherit, self).cart(**post)


    @http.route('/mask/design/load1/<int:product>/<int:order>/<string:position>', type="http", website=True, auth='public')
    def mask_design_preview1(self, product, order, position, **post):
        rop_color = False
        mask_color = False
        image = False
        product = request.env['product.product'].sudo().search([('id','=',int(product))],limit=1)
        order = request.env['sale.order'].sudo().search([('id','=',int(order))],limit=1)
        # lines = request.env['sale.order'].sudo().search([('id','=',int(order))], limit=1)
        if order:
            image = order.id
        for i in product.product_template_attribute_value_ids:
            if i.attribute_id.name == 'Earloop color':
                rop_color = i.html_color
            if i.attribute_id.name == 'Cloth color':
                mask_color = i.html_color
        # attributes = dict()
        # for ptav in product.product_template_variant_value_ids:
        #     attributes[ptav.attribute_id.name] = ptav.id


        return request.render("mask_cutomization.mask_design_load", {
                        'product': product,
                        'rop_color': rop_color,
                        'mask_color': mask_color,
                        'image': image,
                        'position': position,
                        'area': order.mask_area,
                        'order': order.id,
                        'bg_image': order.upload_your_image,
                        # 'attributes': attributes,

        })