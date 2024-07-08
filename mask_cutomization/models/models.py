
try:
    import qrcode
except ImportError:
    qrcode = None
try:
    import base64
except ImportError:
    base64 = None

from odoo import fields, models, api
from PIL import Image
from odoo.http import request
from odoo.tools import ImageProcess


class ProductSaleOrderLineInherited(models.Model):
    _inherit = 'sale.order'

    upload_your_image = fields.Binary(string='Upload Your Image')
    upload_file_name = fields.Char(string='Upload File Name')
    mask_size = fields.Selection([
        ('adult', 'Adult Mask'),
        ('child', 'Child Mask')
    ], string='Mask Size')
    mask_area = fields.Selection([
        ('logo', 'Logo Mask'),
        ('full', 'Full Mask'),
        ('blank', 'Blank Mask')
    ], string='Mask Area')

    session_product_ids = fields.One2many('product.line','session_product_id', string="Session Product Lines")


class ProductProductSelectInherited(models.Model):
    _inherit = 'product.template'

    is_mask_product = fields.Boolean()
    mask_type = fields.Selection([('korean_style', 'Korean Style'),
                                  ('surgical', 'Surgical'),
                                  ('foldable', 'Foldable')], string='Mask Type')
    is_nose_pad = fields.Boolean()
    description_offer_qty = fields.Char(default='HK$1300 / 1000pcs')
    description_offer_box = fields.Char(default='MOQ: 1 box / 1000pcs')
    features = fields.Html(string='Features', store=True, readonly=False)
    discription = fields.Html(string='Description', store=True, readonly=False)
    additional_information = fields.Html(string='Additional Information', store=True, readonly=False)
    discription_chinese = fields.Html(string='Chinese Description', store=True, readonly=False)
    nose_pad_image = fields.Binary(string='Upload nose pad image')
    logo_image = fields.Binary(string='Upload Logo image')
    full_image = fields.Binary(string='Upload full image')
    blank_image = fields.Binary(string='Upload blank image')
    gltf_file = fields.Binary(string='File Gltf 3d')
    gltf_file_flat = fields.Binary(string='File Gltf 3d Flat')
    default_mask_attribute = fields.Many2one('product.template.attribute.value',string='Default Mask Attribute')
    default_rope_attribute = fields.Many2one('product.template.attribute.value',string='Default Rop Attribute')
    default_fragrance_attribute = fields.Many2one('product.template.attribute.value',string='Default Fragrance Attribute')
    default_nose_attribute = fields.Many2one('product.template.attribute.value',string='Default nose Attribute')

    main_mask_material_name = fields.Char(default='Main_Mask')
    nose_pad_material_name = fields.Char(default='Nose_Pad')
    ear_rope_material_name = fields.Char(default='Ropes')
    parent_logo = fields.Char(default='Logo')
    logo_material_name = fields.Char(default='Logo_Place_holder')
    logo_material_name2 = fields.Char(default='Logo_Place_holder2')
    logo_material_name3 = fields.Char(default='Logo_Place_holder3')
    logo_material_name4 = fields.Char(default='Logo_Place_holder4')
    jaw_pad = fields.Char(default='Jaw_Pad')
    main_mask_back = fields.Char(default='main mask back side')
    main_mask_front = fields.Char(default='main mask front side')
    root_inspection = fields.Boolean(default=True)
    pointed_light = fields.Boolean(default=True)
    ambient_light = fields.Boolean(default=False)
    mask_position_x = fields.Integer(default=0)
    mask_position_y = fields.Integer(default=0)
    mask_position_z = fields.Integer(default=0)
    mask_rotation = fields.Boolean(default=True)
    background_color = fields.Char(default='#FFFFFF')
    repeat_x = fields.Float(default=1.5)
    repeat_y = fields.Float(default=2.2)
    gltf_background_image = fields.Binary(string='Gltf Background image')
    logo_crop_width = fields.Float(default=390)
    logo_crop_height = fields.Float(default=290)
    full_crop_width = fields.Float(default=390)
    full_crop_height = fields.Float(default=290)

    preview_full_area = fields.Binary(string='preview full area')
    preview_logo_area = fields.Binary(string='preview logo area')
    carton_image = fields.Binary(string='Carton Image')
    package_image = fields.Binary(string='Package Image')
    shelf_life = fields.Float(default=6)
    # full = fields.Binary(string='Package Image')

    packaging_box_per_carton = fields.Integer(string='Packaging box per carton', default=20)
    packaging_box_per_qty = fields.Integer(string='Packaging box per qty', default=20)

    package_image_width = fields.Float(string='Package image width (px)', default=140)
    package_image_height = fields.Float(string='Package image height (px)', default=80)
    carton_image_width = fields.Float(string='Carton image width (px)', default=160)
    carton_image_height = fields.Float(string='Carton image height (px)', default=60)

    @api.model
    def get_editor_image(self, product_id):
        if product_id:
            pro = self.env['product.template'].sudo().search([('id','=',int(product_id))])
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

    def generate_product_sku(self):
        for product in self.product_variant_ids:
            if not product.default_code:
                product.generate_sku()
                self._cr.commit()


class SaleOrderLineInherited(models.Model):
    _inherit = 'sale.order.line'

    packaging_image = fields.Binary(string='Packaging Logo')
    package_upload_file_name = fields.Char(string='Upload File Name')
    carton_packaging_image = fields.Binary(string='Packaging Logo')
    carton_upload_file_name = fields.Char(string='Upload File Name')
    nose_pad_product = fields.Many2one('product.product',string='Nose Pad Product')
    upload_your_image = fields.Binary(string='Upload Your Image')
    upload_file_name = fields.Char(string='Upload File Name')
    mask_size = fields.Selection([
        ('adult', 'Adult Mask'),
        ('child', 'Child Mask')
    ], string='Mask Size')
    mask_area = fields.Selection([
        ('logo', 'Logo Mask'),
        ('full', 'Full Mask'),
        ('blank', 'Blank Mask')
    ], string='Mask Area')
    price_nose_pad = fields.Float(string="nose pad extra price")

    def _image_size_calculate(self):
        if self.packaging_image:
            image = ImageProcess(self.packaging_image)
            w, h = image.image.size
            return {
                'width': format(w * 0.26458333333333,".2f"),
                'height': format(h * 0.26458333333333,".2f")
            }
        return False

    def _image_size_carton_calculate(self):
        if self.carton_packaging_image:
            image = ImageProcess(self.carton_packaging_image)
            w, h = image.image.size
            return {
                'width': format(w * 0.26458333333333,".2f"),
                'height': format(h * 0.26458333333333,".2f")
            }
        return False

    def _get_product_colour(self):
        if self.product_id:
            for i in self.product_id.product_template_attribute_value_ids:
                if i.attribute_id.name == 'Mask color':
                    return i.name
        return False


class ProductPackagingInherited(models.Model):
    _inherit = 'product.packaging'

    package_image = fields.Binary(string='Package image')
    carton_image = fields.Binary(string='Carton image')
    carton_package = fields.Boolean(string='is a carton package')


class ProductProductSelectInherited(models.Model):
    _inherit = 'auth.oauth.provider'

    logo = fields.Binary(string='Logo')


class SaleConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    nose_product = fields.Many2one('product.template')
    main_mask_material_name = fields.Char(default='Main_Mask')
    nose_pad_material_name = fields.Char(default='Nose_Pad')
    ear_rope_material_name = fields.Char(default='Ropes')
    logo_material_name = fields.Char(default='Logo')
    jaw_pad = fields.Char(default='Jaw_Pad')
    root_inspection = fields.Boolean(default=True)
    website_price_list = fields.Many2one('product.pricelist')

    def get_values(self):
        res = super(SaleConfig, self).get_values()
        res.update(
            nose_product=int(self.env['ir.config_parameter'].sudo().get_param('mask_cutomization.nose_product')),
            website_price_list=int(self.env['ir.config_parameter'].sudo().get_param('mask_cutomization.website_price_list')),
        )
        return res

    def set_values(self):
        super(SaleConfig, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        nose_product = self.nose_product.id
        website_price_list = self.website_price_list.id
        param.set_param('mask_cutomization.nose_product', nose_product)
        param.set_param('mask_cutomization.website_price_list', website_price_list)



class WebsiteFormConfigServiceProduct(models.Model):
    _inherit = 'website'



    def _website_service_product(self):
        pro = int(self.env['ir.config_parameter'].sudo().get_param('mask_cutomization.nose_product'))
        if pro:
            temp = self.env['product.product'].sudo().search([('product_tmpl_id','=',pro)], limit=1)
            return temp
        else:
            return False


class SessionProductLine(models.Model):
    _name = 'product.line'
    _description = "Product Lines"

    name = fields.Char(string='Name')
    session_product_id = fields.Many2one('sale.order', string="product Line Id")
    product_id = fields.Many2one('product.product', string="Product")
    qty = fields.Integer(string="qty")
    buffer_image = fields.Binary(string='Full Image')
    buffer_image_name = fields.Char(string='Full Image Name')
    packaging_image = fields.Binary(string='Package Image')
    packaging_image_name = fields.Char(string='Package Image Name')
    carton_packaging_image = fields.Binary(string='Carton Image')
    carton_upload_file_name = fields.Char(string='Carton Image Name')
    product_packaging_id = fields.Many2one('product.packaging', string='Product Packaging')
    is_nosepad = fields.Boolean(string="is Nose Pad")
    price_nose_pad = fields.Float(string="Nose Pad Price")

    def _image_size_calculate(self):
        if self.packaging_image:
            image = ImageProcess(self.packaging_image)
            w, h = image.image.size
            return {
                'width': format(w * 0.26458333333333,".2f"),
                'height': format(h * 0.26458333333333,".2f")
            }
        return False

    def _image_size_default_calculate(self):
        if self.product_id.product_tmpl_id:
            # image = ImageProcess(self.product_id.product_tmpl_id)
            # w, h = image.image.size
            w = self.product_id.product_tmpl_id.package_image_width
            h = self.product_id.product_tmpl_id.package_image_height
            print("iiiii",w,h)
            return {
                'width': format(w * 0.26458333333333,".2f"),
                'height': format(h * 0.26458333333333,".2f")
            }
        return False

    def _image_size_default_carton_calculate(self):
        if self.product_id.product_tmpl_id:
            # image = ImageProcess(self.product_id.product_tmpl_id)
            # w, h = image.image.size
            w = self.product_id.product_tmpl_id.carton_image_width
            h = self.product_id.product_tmpl_id.carton_image_height
            print("iiiii",w,h)
            return {
                'width': format(w * 0.26458333333333,".2f"),
                'height': format(h * 0.26458333333333,".2f")
            }
        return False
    def _image_size_carton_calculate(self):
        if self.carton_packaging_image:
            image = ImageProcess(self.carton_packaging_image)
            w, h = image.image.size
            return {
                'width': format(w * 0.26458333333333,".2f"),
                'height': format(h * 0.26458333333333,".2f")
            }
        return False

    def _get_product_colour(self):
        print("product line")
        import re
        if self.product_id:
            for i in self.product_id.product_template_attribute_value_ids:
                if i.attribute_id.name == 'Cloth color':
                    a = i.name
                    print("color",a)
                    try:
                        ch = "/"
                        strValue = i.name.split(ch, 1)[0]
                        return strValue
                    except Exception as e:
                        return a

        return False

    def _get_product_colour_code(self):
        if self.product_id:
            for i in self.product_id.product_template_attribute_value_ids:
                if i.attribute_id.name == 'Cloth color':
                    return i.html_color
        return False

    def _get_carton_details(self):
        details = dict()
        if self.product_id:
            details['exp'] = self.product_id.shelf_life
            details['qty'] = 200
            details['nt_wt'] = 200 * (self.product_id.weight if self.product_id.weight else 0.005)
            details['gr_wt'] = 200 * (self.product_id.weight if self.product_id.weight else 0.005)
        return details


class ResPartnerUser(models.Model):
    _inherit = 'res.users'

    phone_code = fields.Char(related='partner_id.phone_code', inherited=True, readonly=False)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    phone_code = fields.Char()

    def language_get(self):

        return


class PortalWebsite(models.Model):
    _inherit = 'website'


    def language_get(self):
        return [(lg.code, lg.url_code, lg.name) for lg in self.language_ids]
