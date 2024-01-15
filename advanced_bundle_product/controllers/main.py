# -*- coding: utf-8 -*-
from odoo import http,_
import json
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website.controllers.main import Website
# from werkzeug.exceptions import Forbidden
import logging

_logger = logging.getLogger(__name__)


class WebsiteCustom(Website):
    @http.route()
    def publish(self, id, object):
        flag = False
        if object == 'product.template':
            product_template = request.env[object].sudo().browse(id)
            for product in product_template.product_variant_ids:
                if product.in_bundle:
                    flag = True
            if flag == True:
                return 'in_bundle'       
        res = super().publish(id,object)
        return res

class AdvancedBundleSale(WebsiteSale):
    @http.route(['/shop/bundle/product'], type='json', auth="public", website=True, csrf=False)
    def cart_collection_update(self, data, **kw):
        bundle_id, *bundled_products = data
        order_id = request.website.sale_get_order(force_create=True)
        website = request.env['website'].get_current_website()
        
        if order_id and bundle_id:
            product = request.env['product.product'].sudo().browse(bundle_id[0])
            vals = {
                    'order_id':order_id.id,'product_id':product.id,'name':product.display_name, 'price_unit':kw.get('total_price'),'product_uom':1,'product_uom_qty':bundle_id[1]
                     }
            line_id = request.env['sale.order.line'].sudo().create(vals)
            for record_id,qty,price,original_price in bundled_products:
                product = request.env['product.product'].sudo().browse(record_id)
                val = {'product_id':product.id, 'price_unit':price,'product_uom_qty':qty,'original_qty':qty,'currecny_id':website.currency_id.id,'original_price':original_price}
                line_id.advance_bundle_order_lines = [(0,0,val)]
        
        return True
    
    @http.route()
    def shop_payment(self,**post):
        """Over-rider shop payment Controller"""
        order = request.website.sale_get_order(force_create=True,update_pricelist=False)
        res = super().shop_payment(**post)
        return res
		
    @http.route()
    def cart_update_json(self, product_id, line_id=None, add_qty=None, set_qty=None, display=True):
        bundle_product_line_id = request.env['sale.order.line'].sudo().browse(line_id)
        for rec in bundle_product_line_id.advance_bundle_order_lines:
            qty = rec.original_qty*set_qty
            rec.product_uom_qty = qty
        res = super().cart_update_json(product_id, line_id, add_qty, set_qty, display)
        return res

    @http.route(["/website/wk_lang"], type='json', auth="public", methods=['POST'], website=True)
    def website_langauge(self, code, **kw):
        lang_id = request.env['res.lang'].search([('code', '=', code.replace('-', '_'))])
        
        return {
        'sep_format': lang_id.grouping,
        'decimal_point': lang_id.decimal_point,
        'thousands_sep': lang_id.thousands_sep
        }

    @http.route()
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        product = request.env['product.product'].sudo().browse(int(product_id))
        if product.product_tmpl_id.is_advance_bundle:
            return request.redirect("/shop/product/"+str(product.product_tmpl_id.id))    
        res = super().cart_update(product_id,add_qty,set_qty,**kw)
        return res


    @http.route('/bundle/product',auth='public',website=True,type="http")
    def demo_bundle_product(self):
        demo_bundle_product = request.env.ref('advanced_bundle_product.advanced_bundle_1_product_template').id
        redirect_url = '/shop/product/{}'.format(str(demo_bundle_product))
        return request.redirect(redirect_url)
