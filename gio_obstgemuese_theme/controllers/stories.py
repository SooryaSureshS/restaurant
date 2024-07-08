from odoo import http
from odoo.addons.website_blog.controllers.main import WebsiteBlog


class WebsiteBlogInherit(WebsiteBlog):

    @http.route()
    def blog(self, blog=None, tag=None, page=1, search=None, **opt):
        """
        Route handler for blog pages.

        This function extends the functionality of the parent class's blog
        method to set a custom template for the response.

        :param blog: (optional) the blog id to display
        :param tag: (optional) the tag to filter blog posts by
        :param page: (optional) the page number to display
        :param search: (optional) a string to search blog posts for
        :param opt: (optional) additional options
        :return: the response object with the custom template set
        """
        res = super(WebsiteBlogInherit, self).blog(blog=blog, tag=tag, page=page, search=search, **opt)
        setattr(res, 'template', 'gio_obstgemuese_theme.obst_stories')
        return res
