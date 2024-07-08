# -*- coding: utf-8 -*-
import logging
from odoo import http, _
from odoo.http import request
from odoo.addons.website_sale.controllers import main
import xml.etree.ElementTree as ET
from xml.dom import minidom
import ftplib
from tempfile import gettempdir
import os
from PIL import Image
import requests
from io import BytesIO
import base64
from werkzeug.urls import url_join
import json

_logger = logging.getLogger(__name__)

DATA_LIS = ['POCode', 'Revision', 'IssueDate', 'AirShipDate', 'SeaShipDate', 'CancelDate', 'LabelName', 'Reference',
            'PaymentTerm', 'DeliveryTerm', 'ShipmentMode', 'Comments', 'EndBuyer', 'EndBuyerCountry', 'Status', 'Line']
LINE_LIS = ['Style', 'Color', 'Size', 'SKU', 'Quantity', 'Price', 'Imgfile1', 'Imgfile2', 'Imgfile3', 'Imgfile4',
            'Imgfile5']


class WebsiteSaleInherit(main.WebsiteSale):

    @http.route()
    def shop_payment(self, **post):
        order = request.website.sale_get_order()
        carrier_id = post.get('carrier_id')
        keep_carrier = post.get('keep_carrier', False)
        if keep_carrier:
            keep_carrier = bool(int(keep_carrier))
        if carrier_id:
            carrier_id = int(carrier_id)
        if order:
            order.with_context(keep_carrier=keep_carrier)._check_carrier_quotation(force_carrier_id=carrier_id)
            if carrier_id:
                return request.redirect("/shop/payment")

        return super(WebsiteSaleInherit, self).shop_payment(**post)

    def _get_xml_string(self, order, file_name):
        root = ET.Element("SkyproPO")
        ET.SubElement(root, 'POCode').text = self.get_po_code(order)
        ET.SubElement(root, 'Revision').text = "1"
        ET.SubElement(root, 'IssueDate').text = str(order.date_order.date())
        ET.SubElement(root, 'AirShipDate').text = str(
            order.picking_ids.date_deadline.date() if order.picking_ids else str(order.date_order.date()))
        ET.SubElement(root, 'SeaShipDate').text = str(
            order.picking_ids.date_deadline.date() if order.picking_ids else str(order.date_order.date()))
        ET.SubElement(root, 'CancelDate').text = str(order.date_order.date())
        ET.SubElement(root, 'LabelName').text = "Skypro"
        ET.SubElement(root, 'Reference').text = order.partner_id.name
        ET.SubElement(root, 'PaymentTerm').text = "T/T"
        # ET.SubElement(root, 'PaymentTerm').text = order.payment_term_id.code
        ET.SubElement(root, 'DeliveryTerm').text = "DDT"
        # ET.SubElement(root, 'DeliveryTerm').text = str(order.picking_ids.carrier_id.code if order.picking_ids else "")
        ET.SubElement(root, 'ShipmentMode').text = "01"
        # ET.SubElement(root, 'ShipmentMode').text = str(order.picking_ids.shipping_term_id.code if order.picking_ids else "")
        ET.SubElement(root, 'Comments').text = ""
        ET.SubElement(root, 'EndBuyer').text = order.partner_invoice_id.name if order.partner_invoice_id and order.partner_invoice_id.name else order.partner_id.name if order.partner_id.name else ""
        ET.SubElement(root, 'EndBuyerCountry').text = "HK"
        # ET.SubElement(root, 'EndBuyerCountry').text = order.partner_id.country_id.code
        ET.SubElement(root, 'Status').text = "1"
        ET.SubElement(root, 'BillingContact').text = order.partner_invoice_id.name if order.partner_invoice_id and order.partner_invoice_id.name else ""
        ET.SubElement(root, 'BillingPhone').text = ((order.partner_invoice_id.phone_code+"-") if order.partner_invoice_id and order.partner_invoice_id.phone_code else "") + (order.partner_invoice_id.phone if order.partner_invoice_id and order.partner_invoice_id.phone else "")
        ET.SubElement(root, 'BillingAddress').text = (order.partner_invoice_id.street if order.partner_invoice_id and order.partner_invoice_id.name else "") + ((", " + order.partner_invoice_id.city) if order.partner_invoice_id.city else "")
        ET.SubElement(root, 'DeliveryContact').text = order.partner_shipping_id.name if order.partner_shipping_id and order.partner_shipping_id.name else ""
        ET.SubElement(root, 'DeliveryPhone').text = ((order.partner_shipping_id.phone_code+"-") if order.partner_shipping_id and order.partner_shipping_id.phone_code else "") + (order.partner_shipping_id.phone if order.partner_shipping_id and order.partner_shipping_id.phone else "")
        ET.SubElement(root, 'DeliveryAddress').text = (order.partner_shipping_id.street if order.partner_shipping_id and order.partner_shipping_id.name else "") + ((", " + order.partner_shipping_id.city) if order.partner_shipping_id.city else "")
        order_lis, file_transfer_details = self.website_sale_order_get(order)
        for rec in order_lis:
            line = ET.SubElement(root, 'Line')
            ET.SubElement(line, 'Style').text = str(rec.get('style'))
            ET.SubElement(line, 'Color').text = str(rec.get('color'))
            ET.SubElement(line, 'Size').text = str(rec.get('size'))
            ET.SubElement(line, 'SKU').text = str(rec.get('sku'))
            ET.SubElement(line, 'Quantity').text = str(rec.get('quantity'))
            ET.SubElement(line, 'Price').text = str(rec.get('price'))
            ET.SubElement(line, 'Imgfile1').text = str(rec.get('Imgfile1')[0] if rec.get('Imgfile1') else "")
            ET.SubElement(line, 'Imgfile2').text = str(rec.get('Imgfile2')[0] if rec.get('Imgfile2') else "")
            ET.SubElement(line, 'Imgfile3').text = str(rec.get('Imgfile3')[0] if rec.get('Imgfile3') else "")
            ET.SubElement(line, 'Imgfile4').text = str(rec.get('Imgfile4')[0] if rec.get('Imgfile4') else "")
            ET.SubElement(line, 'Imgfile5').text = str(rec.get('Imgfile5')[0] if rec.get('Imgfile5') else "")
        ET.ElementTree(root)
        pretty_xml_as_string = minidom.parseString(
            ET.tostring(root)).toprettyxml(indent="   ")
        file_path = os.path.join(gettempdir(), file_name)
        f = open(file_path, "w")
        f.write(pretty_xml_as_string)
        f.close()
        file_transfer_details.append({"name": file_name, "file": file_path, "file_type": "xml"})
        return file_transfer_details

    @staticmethod
    def _file_transfer(image_details):
        def transfer_file(xml_directory, image_directory, file_name, file_path, file_type):
            if file_type == 'xml':
                session.cwd(xml_directory)
            if file_type == 'image':
                session.cwd(image_directory)
            session.storbinary('STOR ' + file_name, open(file_path, "rb"))
            _logger.info("::::::: File Transfered :::::::: ")
        ftp_ip_address = request.env['ir.config_parameter'].sudo().get_param('ftp_skypro.ftp_ip_address')
        ftp_user_name = request.env['ir.config_parameter'].sudo().get_param('ftp_skypro.ftp_user_name')
        ftp_password = request.env['ir.config_parameter'].sudo().get_param('ftp_skypro.ftp_password')
        ftp_image_directory = request.env['ir.config_parameter'].sudo().get_param('ftp_skypro.ftp_image_directory')
        ftp_xml_directory = request.env['ir.config_parameter'].sudo().get_param('ftp_skypro.ftp_xml_directory')
        _logger.info("::::::: Connecting TO Remote Server ::::::::")
        session = ftplib.FTP(ftp_ip_address, ftp_user_name, ftp_password, timeout=200)
        _logger.info("::::::: Transfering Sale Order TO Remote Server :::::::")
        session.encoding = "utf-8"
        for rec in image_details:
            if rec:
                transfer_file(ftp_xml_directory, ftp_image_directory, rec.get('name'), rec.get('file'),
                              rec.get('file_type'))
        session.quit()

    @http.route(['/shop/confirmation'], type='http', auth="public", website=True, sitemap=False)
    def shop_payment_confirmation(self, **post):
        res = super(WebsiteSaleInherit, self).shop_payment_confirmation(**post)
        use_ftp = request.env['ir.config_parameter'].sudo().get_param('ftp_skypro.use_ftp')
        if not use_ftp:
            return res
        sale_order_id = request.session.get('sale_last_order_id')
        if not sale_order_id:
            return res
        order = request.env['sale.order'].sudo().browse(sale_order_id)
        file_name = '%s.xml' % (self.get_po_code(order))
        # product_pack_image = request.env['ir.config_parameter'].sudo().get_param('ftp_skypro.product_pack_image')
        # product_carton_image = request.env['ir.config_parameter'].sudo().get_param('ftp_skypro.product_carton_image')
        try:
            file_transfer_details = self._get_xml_string(order, file_name)
            self._file_transfer(file_transfer_details)
        except Exception as e:
            _logger.info(f"::::::: {e} :::::::: ")
        return res

    @http.route('/ftp/upload', type='json', auth="public", methods=['POST', 'GET'], csrf=False)
    def ftp_upload(self):
        data = request.httprequest.data
        print(data)
        data = json.loads(data)
        use_ftp = request.env['ir.config_parameter'].sudo().get_param('ftp_skypro.use_ftp')
        if not use_ftp:
            return {'success': False, 'message': 'FTP is OFF'}
        sale_order_id = data.get('sale_order_id')
        if not sale_order_id:
            return {'success': False, 'message': 'Order not found'}
        order = request.env['sale.order'].sudo().browse(sale_order_id)
        file_name = '%s.xml' % (self.get_po_code(order))
        # product_pack_image = request.env['ir.config_parameter'].sudo().get_param('ftp_skypro.product_pack_image')
        # product_carton_image = request.env['ir.config_parameter'].sudo().get_param('ftp_skypro.product_carton_image')
        try:
            file_transfer_details = self._get_xml_string(order, file_name)
            self._file_transfer(file_transfer_details)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'message': e}

    @staticmethod
    def get_po_code(order):
        date = order.date_order
        month = str(date.month) if len(str(date.month)) == 2 else "0"+str(date.month)
        day = str(date.day) if len(str(date.day)) == 2 else "0"+str(date.day)
        return "E" + str(date.year)[2:] + month + day + order.name[-5:]

    @staticmethod
    def get_shipping_address(order):
        return order.partner_id.name if order.partner_id.name else "" + " " + order.partner_id.street if order.partner_id.street else "" + " " + order.partner_id.city if order.partner_id.city else "" + " " + order.partner_id.state_id.name if order.partner_id.state_id else "" + " " + order.partner_id.country_id.name if order.partner_id.country_id else "" + " " + order.partner_id.zip if order.partner_id.zip else ""

    @staticmethod
    def website_sale_order_get(sale_order):
        def get_xml_style(order_line):
            return order_line.product_id.default_code[:3]

        def get_color(order_line):
            return order_line.product_id.default_code[3:11]

        def get_size(order_line):
            return order_line.product_id.default_code[11:12]

        def get_po_code(order):
            date = order.date_order
            return "E" + str(date.year)[2:] + str(date.month) + str(date.day) + order.name[-5:]

        def get_image_file_tiff(sale_ord, image_data, data, num):
            if image_data:
                file_name = get_po_code(sale_ord)
                img = Image.open(BytesIO(base64.b64decode(image_data)))
                file_path = os.path.join(gettempdir(), f"{file_name}-{str(num)}{data[-1:]}.tiff")
                img.save(file_path)
                return f"{file_name}-{str(num)}{data[-1:]}.tiff", file_path
            return ""

        order_lis = []
        optional_products = [line for line in sale_order.order_line if line.linked_line_id]
        val = {}
        count = 0
        for rec in sale_order.order_line:
            if rec.product_template_id.purchase_ok:
                count = (count + 1) if rec not in optional_products else count
                val[rec.id] = {'style': get_xml_style(rec), 'color': get_color(rec),
                               'size': get_size(rec), 'sku': rec.product_id.default_code,
                               'quantity': rec.product_uom_qty, 'price': rec.price_unit,
                               'Imgfile1': get_image_file_tiff(sale_order, rec.upload_your_image if rec.mask_area=="logo" else False, "image1", count),
                               'Imgfile2': get_image_file_tiff(sale_order, rec.upload_your_image if rec.mask_area=="full" else False, 'image2', count),
                               'Imgfile3': get_image_file_tiff(sale_order, rec.packaging_image, 'image3', count),
                               'Imgfile4': get_image_file_tiff(sale_order, rec.carton_packaging_image, 'image4', count),
                               'Imgfile5': get_image_file_tiff(sale_order, False, 'image5', count)}
        [order_lis.append(x) for x in [n for n in val.values()]]
        image_del = [[{"name": (order.get(ele)[0]), "file": (order.get(ele)[1]), "file_type":"image"} if order.get(ele) else {} for ele in
                      ['Imgfile1', 'Imgfile2', 'Imgfile3', 'Imgfile4', 'Imgfile5']] for order in order_lis]
        image_details = []
        for lis in image_del:
            image_details.extend(lis)
        return order_lis, image_details


class OAuthTiffController(http.Controller):

    @http.route(['/ftp/skypro/<string:id>/<string:field>/<string:file_name>'], type='http', auth='public')
    def _get_tiff_image_link(self, id, field):
        sale_order_line_obj = request.env['sale.order.line'].sudo().search([('id', '=', int(id))])
        status, headers, image_base64 = request.env['ir.http'].sudo().binary_content(
            model='sale.order.line', id=sale_order_line_obj.id, field=field,
            default_mimetype='image/png')
        return request.env['ir.http']._content_image_get_response(status, headers, image_base64)
