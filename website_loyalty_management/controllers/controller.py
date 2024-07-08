
from odoo import SUPERUSER_ID
from odoo import http
from odoo.http import route,request
from odoo.tools.translate import _
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.portal.controllers.portal import CustomerPortal as WebsiteAccount, pager as portal_pager
import logging
_logger = logging.getLogger(__name__)

class website_loaylty_management(http.Controller):

    def validate_redeem(self,post,values,loyalty_obj,partner_id,sale_order):
        redeem_rule_id=loyalty_obj._get_redeem_rule_id(partner_id)
        if not redeem_rule_id:
            values['no_redeem_rule_match'] =True

        elif not redeem_rule_id.reward:
            values['no_reward_rule'] =True
        else:
            res=self._allowed_redeem(partner_id ,loyalty_obj ,redeem_rule_id,sale_order,values)
            if res:
                values.update(res)
        return values


    @http.route(['/loyalty/confirmation/'] ,type = 'json' ,auth = "public" ,website = True )
    def get_confimation(self , **post ):
        values = dict()
        partner_id= request.env.user.partner_id
        website = request.website
        sale_order =  website.sale_get_order()
        sale_order.wk_loyalty_program_id=request.env['website'].sudo().get_current_website().wk_loyalty_program_id.id
        loyalty_obj = website.get_active_loyalty_obj(sale_order=sale_order)

        if request.env.user.id != request.env.ref('base.public_user').id:
            values['login'] = True
            if not sale_order or not len(sale_order) or sale_order.amount_total==0:
                values['no_order'] = True
            elif  partner_id.wk_website_loyalty_points<1:
                values['no_point'] = True
            elif not loyalty_obj.redeem_rule_list:
                values['no_redeem_rule'] = True
            else:
                rule = loyalty_obj.redeem_rule_list
                all_rule = []
                for i in rule:
                    if i.product_ids:
                        if partner_id.wk_website_loyalty_points>=i.point_start:
                            all_rule.append({'products': [{'product_id':k.id,'product_name':k.name} for k in i.product_ids],'line_id':i.id, 'points_start': int(i.point_start)})
                if len(all_rule)<1:
                    values['all_rule']= False
                    values['all_rule_message']= True
                else:
                    values['all_rule'] = all_rule
                    values['allowed_redeem'] = True

        return request.env['ir.ui.view']._render_template("website_loyalty_management.message_template", values)

    # def _allowed_redeem(self ,partner_id ,loyalty_obj ,redeem_rule_id ,sale_order,values ):
    #     reward = redeem_rule_id.reward
    #     sale_order_amount = sale_order.amount_total
    #
    #     computed_amount = partner_id.wk_website_loyalty_points*reward
    #     max_redeem_amount = loyalty_obj.max_redeem_amount
    #
    #     eligible_amount = computed_amount < max_redeem_amount and computed_amount  or     max_redeem_amount
    #     reduced_amount = sale_order_amount  < eligible_amount and sale_order_amount  or      eligible_amount
    #     diff=sale_order_amount < eligible_amount and sale_order_amount or   eligible_amount
    #     values['reduced_amount'] = reduced_amount
    #     values['reduced_point'] = reward and reduced_amount/reward
    #     values['allowed_redeem'] = 'partial_redeem'
    #     if loyalty_obj.redeem_policy == 'one_time_redeem':
    #         values['allowed_redeem'] = 'one_time_redeem'
    #         percent_benefit = round((diff*100/eligible_amount),2)
    #         values['percent_benefit'] =percent_benefit
    #     return values

    @http.route(['/loyality/get_reward/'] ,type = 'json' ,auth = "public" ,website = True )
    def get_reward(self ,**post ):
        # result=request.website.get_rewards(request.website.sale_get_order())
        order = request.website.sale_get_order()
        order_line = {'product_id':int(post.get('product_id')),'product_uom_qty':1,'name':'loyalty free','price_unit':0,'order_id':order.id}
        pro = request.env['sale.order.line'].sudo().create(order_line)

        History = request.env['website.loyalty.history'].sudo()
        vals = {
            'loyalty_id': order.wk_loyalty_program_id.id,
            'partner_id': order.partner_id.id,
            'points_processed':float(post.get('points_end')) ,
            'sale_order_ref': order.id,
            'redeem_amount': pro.product_id.list_price,
            'loyalty_process': 'deduction',
            'process_reference': 'Sale Order',
        }
        history=History.create(vals)
        pro.loyalty_id=history.id

        return True
        # if result.get('reward_amount'):
        #     request.session['reward']='Taken'
        #     request.session['reward']=result.get('reward_amount')
        # return request.redirect("/shop/cart/")



class WebsiteAccount(WebsiteAccount):
    @http.route(['/my/loyalty', '/my/loyalty/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_loyalty(self, page=1, **kw):
        HistorySudo = request.env['website.loyalty.history'].sudo()
        rule = request.env['reward.redeem.rule'].sudo().search([])
        user = request.env.user
        domain = [('partner_id', '=', user.partner_id.id)]
        loyalty_count = HistorySudo.search_count(domain)
        pager = portal_pager(
            url="/my/loyalty",
            total=loyalty_count,
            page=page,
            step=self._items_per_page
        )
        all_rule = []
        for i in rule:
            if i.product_ids:
                all_rule.append({'product_name':i.product_ids.mapped('name'),'points_end':i.point_start})

        histories = HistorySudo.search(domain, limit=self._items_per_page, offset=pager['offset'])
        values = {
                'histories': histories.sudo(),
                'page_name': 'loyalty',
                'pager': pager,
                'all_rule':all_rule,
                'default_url': '/my/loyalty',
                'wk_website_loyalty_points': round(user.wk_website_loyalty_points)
            }
        return  request.render("website_loyalty_management.reward_loyalty", values)

# class WebsiteSale(WebsiteSale):
    # @http.route('/shop/payment/get_status/<int:sale_order_id>' ,type='json' ,auth="public", website=True )
    # def payment_get_status(self ,sale_order_id ,**post):
    #     response=super(WebsiteSale,self).payment_get_status(sale_order_id ,**post)
    #     order=request.env['sale.order'].sudo().browse(sale_order_id)
    #
    #     loyalty_obj =request.website.get_active_loyalty_obj(sale_order=order)
    #     if len(loyalty_obj):
    #         res=loyalty_obj.update_partner_loyalty(order,'draft')
    #         loyalty_obj._save_redeem_history(order)
    #     request.session['reward']=''
    #     return response


    # def remove_loyalty_txn_id(self):
    #     order = request.website.sale_get_order()
    #     if order:
    #         virtual_line=order.order_line.filtered(lambda line:line.is_virtual and (line.virtual_source=='wk_website_loyalty'))
    #         wk_website_loyalty_points = sum(virtual_line.mapped('redeem_points'))
    #         order.partner_id.wk_website_loyalty_points +=wk_website_loyalty_points
    #         virtual_line.unlink()
    #         request.session['reward'] = ''
    #     return True

    #
    # @http.route(['/shop/change_pricelist/<model("product.pricelist"):pl_id>'], type='http', auth="public", website=True)
    # def pricelist_change(self, pl_id, **post):
    #     self.remove_loyalty_txn_id()
    #     res = super(WebsiteSale,self).pricelist_change(pl_id,**post)
    #     return res

    #
    # @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True, csrf=False)
    # def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
    #     self.remove_loyalty_txn_id()
    #     res = super(WebsiteSale,self).cart_update(product_id, add_qty, set_qty, **kw)
    #     return res
    #
    # @http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True)
    # def cart_update_json(self, product_id, line_id, add_qty=None, set_qty=None, display=True):
    #     self.remove_loyalty_txn_id()
    #     res  = super(WebsiteSale,self).cart_update_json(product_id, line_id, add_qty, set_qty, display)
    #     return res

    # @http.route(['/shop/confirmation'], type='http', auth="public", website=True)
    # def payment_confirmation(self, **post):
    #     response=super(WebsiteSale,self).payment_confirmation(**post)
    #     order = response.qcontext.get('order')
    #     if order:
    #         response.qcontext['wk_website_loyalty_points']=order.wk_website_loyalty_points
    #     return response

    # @http.route(['/remove/virtualproduct/<temp>'] ,type='http' ,auth="public" ,website=True )
    # def virtual_product_remove(self, temp):
    #     virtual_line=request.env['sale.order.line'].sudo().search(
    #         [('id', '=', temp),('virtual_source','=','wk_website_loyalty')]
    #     )
    #     if virtual_line:
    #         order = virtual_line.order_id
    #         virtual_line.order_partner_id.wk_website_loyalty_points += virtual_line.redeem_points
    #         virtual_line.unlink()
    #         request.session['reward'] = ''
    #         request.env['website.loyalty.management'].sudo().cancel_redeem_history(order)
    #     return request.redirect("/shop/cart/")
