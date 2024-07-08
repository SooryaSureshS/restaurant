from odoo import models
from bs4 import BeautifulSoup
from odoo.tools.json import scriptsafe


class WebsiteCoverPropertiesMixinInherit(models.AbstractModel):
    _inherit = 'website.cover_properties.mixin'

    def _get_website_image_url(self):
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
        properties = scriptsafe.loads(self.cover_properties)
        base_url = self.get_base_url()
        img = properties.get('background-image', "none").replace('url(', '').replace(')', '').replace('\ ', '').replace("\'", '')
        return img

    def _get_post_content(self):
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
        content = self.content
        soup = BeautifulSoup(content, "html.parser")
        text = soup.get_text().replace('\n', '')
        content_text = ' '.join(text.split()[:54])
        return content_text + '...'
    
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
        content = self.content
        soup = BeautifulSoup(content, "html.parser")
        text = soup.get_text().replace('\n', '')
        content_text = ' '.join(text.split()[:54])
        return content_text + '...'
