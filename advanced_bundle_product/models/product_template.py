# -*- coding: utf-8 -*-
##########################################################################
# Author : Webkul Software Pvt. Ltd. (<https://webkul.com/>;)
# Copyright(c): 2017-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>;
##########################################################################


from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.http import request
import datetime
import logging


from odoo.addons import decimal_precision as dp

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = "product.template"
    is_advance_bundle = fields.Boolean(string='Advance Bundle')
    advance_bundle_line_ids = fields.One2many('advance.bundle.lines',inverse_name='bundle_item')
    bundle_product_currency_id = fields.Many2one('res.currency')

    @api.constrains('is_advance_bundle','advance_bundle_line_ids')
    def check_bundle(self):
        for record in self:
            if (record.is_advance_bundle and len(record.advance_bundle_line_ids) == 0):
                raise UserError("Atleast One product should be added to bundle")
    
    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, parent_combination=False, only_template=False):
        res = super(ProductTemplate,self)._get_combination_info(combination, product_id, add_qty, parent_combination, only_template)
        res.update({'is_advance_bundle':False})
        website = self.env['website'].get_current_website()
        if self.is_advance_bundle:
            price = 0
            for bundle in self.advance_bundle_line_ids:
                if bundle._type in ['required']:
                    for product in bundle.bundle_line_ids:
                        if product.product_name.is_published:
                            converted_price = product.currency_id._convert(product.bundle_price,website.currency_id,website.company_id,datetime.datetime.today(),round=False)
                            price += converted_price

            res['price'] = price
            res.update({'is_advance_bundle':True})
        return res
    
    def _website_show_quick_add(self):
        if self.is_advance_bundle:
            website = self.env['website'].get_current_website()
            bundle_items_price = self._get_bundle_items_price() if self._get_bundle_items_price()>0 else 0
            return self.sale_ok and (not website.prevent_zero_price_sale or self._get_contextual_price()) and bundle_items_price
        return super()._website_show_quick_add()
    
    def _get_bundle_items_price(self):
        website = self.env['website'].get_current_website()
        required_bundle_items = self.mapped('advance_bundle_line_ids').filtered(lambda bundle_line: bundle_line._type=="required")
        items_price = sum(required_bundle_items.mapped('bundle_line_ids').mapped('bundle_price')) if required_bundle_items else 0
        return self.currency_id._convert(items_price,website._get_current_pricelist().currency_id,website.company_id,datetime.datetime.today())



class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    advance_bundle_order_lines = fields.One2many('advance.bundle.order.line', inverse_name='advance_order_line')
    bundle_name = fields.Char()


class SaleOrder(models.Model):
    _inherit="sale.order"

    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, **kwargs):
        values = super(SaleOrder, self)._cart_update(product_id=product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty, **kwargs)
        website_currency = self.currency_id
        order_line_id = self.order_line.filtered(lambda line: line.id==values.get('line_id'))
        if line_id:
            order_line = self._cart_find_product_line(product_id, line_id, **kwargs)[:1]
            total_price = 0
            if order_line.advance_bundle_order_lines:
                for bundle_line_id in order_line.advance_bundle_order_lines:
                    if bundle_line_id.currecny_id:
                        temp = bundle_line_id.currecny_id._convert(bundle_line_id.price_unit,website_currency,self.company_id,datetime.datetime.today(),round=False)
                        bundle_line_id.price_unit = temp
                        total_price += bundle_line_id.price_unit*bundle_line_id.original_qty
                    else:
                        total_price += bundle_line_id.price_unit
                    bundle_line_id.currecny_id = website_currency
                order_line.price_unit = total_price
        
        elif order_line_id.product_id.is_advance_bundle and not order_line_id.advance_bundle_order_lines:
            advance_bundle_line_ids = order_line_id.product_id.mapped('advance_bundle_line_ids').filtered(lambda bundle_line: bundle_line._type=="required")
            advance_bundle_product_items = advance_bundle_line_ids.mapped('bundle_line_ids')
            website = self.env['website'].get_current_website()
            total_price = 0
            bundle_product_items_line = []
            for product in advance_bundle_product_items:
                product_price = product.currency_id._convert(product.bundle_price,website_currency,self.company_id,datetime.datetime.today(),round=False)
                val = {'advance_order_line':order_line_id.id,'product_id':product.id,'price_unit':product_price,'product_uom_qty':product.bundle_qty,'original_qty':product.bundle_qty,'currecny_id':website.currency_id.id}
                bundle_product_items_line.append(val)
                # total_price += product.bundle_qty*product_price (Bundle product price will calculate on their qty)
                total_price += product_price
            self.env['advance.bundle.order.line'].create(bundle_product_items_line)
            order_line_id.price_unit = total_price

        return values



class AdvancedBundleOrderLine(models.Model):
    _name = "advance.bundle.order.line"
    _description = "Advance Bundle Order Line"
    _rec_name = "product_id"

    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)], change_default=True, ondelete='restrict')
    advance_order_line = fields.Many2one('sale.order.line',ondelete='cascade')
    price_unit = fields.Float('Unit Price', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    product_uom_qty = fields.Float(string='Ordered Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True, default=1.0)
    product_image = fields.Binary('Product Image', related="product_id.image_128", store=False, readonly=False)
    original_qty = fields.Float(string='Ordered Quantity Orginal', digits=dp.get_precision('Product Unit of Measure'), default=1.0)
    currecny_id = fields.Many2one('res.currency')
    original_price = fields.Float('Original Unit Price', digits=dp.get_precision('Product Price'), default=0.0)


class StockMove(models.Model):
    _inherit = 'stock.move'

    bundle_name = fields.Char()
