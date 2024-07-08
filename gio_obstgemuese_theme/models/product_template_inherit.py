import base64
from bs4 import BeautifulSoup
from odoo import fields, api, models, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sub_header = fields.Char(string='Sub Header', store=True, readonly=False)
    features = fields.Html(string='Detailed Description', store=True, readonly=False)
    description = fields.Html(string='Description', store=True, readonly=False)
    care_instruction = fields.Html(string='Care Instruction', store=True, readonly=False)
    cover_image = fields.Image(required=True)
    data_sheet_file = fields.Binary(string='Data Sheet', attachment=True)

    @api.model_create_multi
    def create(self, vals_list):
        """
        raise validation error if the website_size_x or y is exceed limit of 4
        """
        if [[val.get(n) for val in vals_list if val.get(n) >= 5] for n in ['website_size_x', 'website_size_y'] if
            [val.get(n) for val in vals_list if val.get(n) >= 5]]:
            raise UserError(
                _('Website Size must be less than 5'))
        return super(ProductTemplate, self).create(vals_list)

    def write(self, vals_list):
        """
        raise validation error if the website_size_x or y is exceed limit of 4
        """
        if [vals_list.get(n) for n in
            list(filter(lambda val: val in [n for n in vals_list.keys()], ['website_size_x', 'website_size_y'])) if
            vals_list.get(n) >= 5]:
            raise UserError(
                _('Website Size must be less than 5'))
        return super(ProductTemplate, self).write(vals_list)

    def _get_cover_image(self):
        """
        return cover image to the template if exist
        """
        self.ensure_one()
        if self.cover_image:
            return [self] + list(self.cover_image) if self.cover_image else []
        else:
            return [self] + list(self.product_template_image_ids)

    def _get_product_features(self):
        """
        Get the URL of the image for a website.

        This function retrieves the URL of the image for a website, by parsing
        the 'cover_properties' field and removing any redundant characters.
        The website is identified by calling the 'ensure_one' method,
        which raises an error if multiple records are selected. The base URL
        of the website is obtained by calling the 'get_base_url' method.

        Returns:
        str: The URL of the image for the website.
        """
        self.ensure_one()
        content = self.features
        soup = BeautifulSoup(content, "html.parser")
        text = soup.get_text().replace('\n', '')
        content_text = ' '.join(text.split())
        return content_text

    def _has_content(self, content):
        """
        Get the URL of the image for a website.

        This function retrieves the URL of the image for a website, by parsing
        the 'cover_properties' field and removing any redundant characters.
        The website is identified by calling the 'ensure_one' method,
        which raises an error if multiple records are selected. The base URL
        of the website is obtained by calling the 'get_base_url' method.

        Returns:
        str: The URL of the image for the website.
        """
        self.ensure_one()
        if content:
            soup = BeautifulSoup(content, "html.parser")
            text = soup.get_text().replace('\n', '')
            content_text = ' '.join(text.split())
            return True if content_text else False
        else:
            return False

    def _get_related_products(self):
        """
        Get the URL of the image for a website.

        This function retrieves the URL of the image for a website, by parsing
        the 'cover_properties' field and removing any redundant characters.
        The website is identified by calling the 'ensure_one' method,
        which raises an error if multiple records are selected. The base URL
        of the website is obtained by calling the 'get_base_url' method.

        Returns:
        str: The URL of the image for the website.
        """
        self.ensure_one()
        domain = [('public_categ_ids', 'in', self.public_categ_ids.ids), ('id', '!=', self.id), ('sale_ok', '=', True),
                  ('detailed_type', '=', 'product')]
        related_products = list(self.sudo().search(domain, limit=4))
        if len(related_products) < 4:
            list(filter((lambda ele: domain.remove(ele)), [('public_categ_ids', 'in', self.public_categ_ids.ids)]))
            related_products.extend(
                list(self.sudo().search(domain, order="id desc", limit=int(4 - (int(len(related_products)))))))
        return related_products

    def _get_data_sheet(self):
        self.ensure_one()
        file_sheet_b64 = base64.b64decode(self.search([('id', '=', 9)]).data_sheet_file)
        return file_sheet_b64



class Product(models.Model):
    _inherit = "product.product"

    def _get_cover_image(self):
        """
        return product template cover image
        """
        self.ensure_one()
        variant_images = list(self.product_variant_image_ids)
        if self.image_variant_1920:
            variant_images = [self] + variant_images
        else:
            variant_images = variant_images + [self]
        return variant_images + self.product_tmpl_id._get_images()[1:]

    def get_product_variants(self, *args):

        pass

