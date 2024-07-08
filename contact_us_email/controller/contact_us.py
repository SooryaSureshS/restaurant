import base64
import werkzeug
from odoo import _, exceptions, http
from odoo.http import request
from odoo.tools import consteq
# from odoo.addons.theme_clarico.controllers.calculate_postage import Website
from odoo.addons.website.controllers.main import Website

class ContactUsInherited(Website):

    @http.route(['/contact_us/confirm'], type='http', auth="public", website=True, csrf=False)
    def contact_us_confirm(self, **kwargs):

        admin_email = "peter@onitburgers.com"
        body_html = '''<div style="margin: 0px; padding: 0px;">
                        <p style="margin: 0px; padding: 0px; font-size: 13px;">
                            Hi ,
                            <br/><br/>
                            A new message from On It Burgers, Please see the below content
                            <br/><br/>
                             <p>
                                    Customer Name: ''' + str(kwargs.get('name')) + '''
                                    </p>
                                    <p>
                                    Email: ''' + str(kwargs.get('email')) + '''
                                    </p>
                                      <p>
                                    Phone: ''' + str(kwargs.get('phone')) + '''
                                    </p>
                                     <p>
                                    Subject: ''' + str(kwargs.get('subject')) + '''
                                    </p>
                                    
                                <br/>
                                <p>
                                Question: ''' + str(kwargs.get('question')) + '''
                                </p>
                                <br/>
                            Thank you
                        </p>
                    </div>'''
        data = {}
        name = kwargs['name']
        email = kwargs['email']
        phone = kwargs['phone']
        subject = kwargs['subject']
        question = kwargs['question']
        data['name'] = name
        data['email'] = email
        data['phone'] = phone
        data['subject'] = subject
        data['question'] = question

        # mail = request.env['ir.mail_server'].sudo().search([], limit=1)
        # mail_from = mail.smtp_user
        # mail_pass = mail.smtp_pass
        # template_obj = request.env['mail.mail'].sudo().search([])
        # template_data = {
        #     'subject': 'A new message from a customer ',
        #     'body_html': body_html,
        #     'email_from': mail_from,
        #     'email_to': admin_email
        # }
        # template_id = template_obj.create(template_data)
        # template_id.sudo().send()

        lead = request.env['crm.lead']

        lead_id = lead.sudo().create({'contact_name': name, 'email_from': email, 'phone': phone,
                                      'name': subject, 'description': question, 'type': 'lead'})

        return request.redirect('/contactus-thank-you')
