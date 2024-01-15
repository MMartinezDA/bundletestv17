# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class AdvanceBundleSaleOrderWizard(models.TransientModel):
    _name = "advance.bundle.product.wizard"
    _description = "Advance Bundle Product Wizard"

    advance_product_id = fields.Many2one('product.product', string='Select Bundle', required=True)
    advance_bundle_qty = fields.Integer('Quantity', default='1')
    advance_bundle_lines = fields.Many2many('advance.bundle.lines', string="Add Bundles Lines")
    advanced_product_items = fields.Many2many('advance.bundle.product.items')
    description = fields.Html(compute='advanced_bundle_description')

    @api.depends('advance_product_id')
    def advanced_bundle_description(self):
        html_data = ''

        if self.advance_product_id:
            html_data = "<table class='table table-striped'>"
            data =  self.advance_product_id.advance_bundle_line_ids
            for record in data:
                if record._type == 'radio':
                    html_data += "<tr><td style='padding:0;overflow: hidden;'><div style='font-size:14px;font-weight: 900;color: white;background-color:#564f4f'>"+record.name+" ::['Single Select' you can select only one product from the list]</div><table class='table table-striped' style='margin-left: 20px;'><thead class='thead-light'><th style='padding:0;'>Product Name</th><th style='padding:0;'>Quantity</th><th style='padding:0;'>Price</th></thead><tbody>"
                elif record._type == 'required':
                    html_data += "<tr><td style='padding:0;overflow: hidden;'><div style='font-size:14px;font-weight: 900;color: white;background-color:#564f4f'>"+record.name+" ::[You have to buy all products from the list]</div><table class='table table-striped' style='margin-left: 20px;'><thead class='thead-light'><th style='padding:0;'>Product Name</th><th style='padding:0;'>Quantity</th><th style='padding:0;'>Price</th></thead><tbody>"
                elif record._type == 'optional':
                    html_data += "<tr><td style='padding:0;overflow: hidden;'><div style='font-size:14px;font-weight: 900;color: white;background-color:#564f4f'>"+record.name+" ::[These are the optional products you can choose if wanted]</div><table class='table table-striped' style='margin-left: 20px;'><thead class='thead-light'><th style='padding:0;'>Product Name</th><th style='padding:0;'>Quantity</th><th style='padding:0;'>Price</th></thead><tbody>"
                elif record._type == 'requiredopt':
                    html_data += "<tr><td style='padding:0;overflow: hidden;'><div style='font-size:14px;font-weight: 900;color: white;background-color:#564f4f'>"+record.name+" ::[If checked you have to select all the products]</div><table class='table table-striped' style='margin-left: 20px;'><thead class='thead-light'><th style='padding:0;'>Product Name</th><th style='padding:0;'>Quantity</th><th style='padding:0;'>Price</th></thead><tbody>"
                elif record._type == 'addon':
                    html_data += "<tr><td style='padding:0;overflow: hidden;'><div style='font-size:14px;font-weight: 900;color: white;background-color:#564f4f'>"+record.name+" ::[These are the Add-On's to the previous products]</div><table class='table table-striped' style='margin-left: 20px;'><thead class='thead-light'><th style='padding:0;'>Product Name</th><th style='padding:0;'>Quantity</th><th style='padding:0;'>Price</th></thead><tbody>"
                elif record._type == 'accessories':
                    html_data += "<tr><td style='padding:0;overflow: hidden;'><div style='font-size:14px;font-weight: 900;color: white;background-color:#564f4f'>"+record.name+" ::[These are the accessories for the selected bundle product]</div><table class='table table-striped' style='margin-left: 20px;'><thead class='thead-light'><th style='padding:0;'>Product Name</th><th style='padding:0;'>Quantity</th><th style='padding:0;'>Price</th></thead><tbody>"

                for rec in record.bundle_line_ids:
                    html_data += "<tr><td style='padding:0;'>"+rec.product_name.display_name+"</td><td style='padding:0;'>"+str(rec.bundle_qty)+"</td><td style='padding:0;'>"+str(rec.bundle_price)+"</td></tr>"
                html_data += "</tbody></table>"

        self.description = html_data+"</table>"


    def add_advance_bundle_button(self):
        sale_order_line = self.env['sale.order.line'].create({'order_id':self._context['active_id'],'product_id':self.advance_product_id.id,'name':self.advance_product_id.name, 'price_unit':self.advance_product_id.list_price,'product_uom':1,'product_uom_qty':self.advance_bundle_qty,'name':self.advance_product_id.name})
        price = 0
        data =  self.advanced_product_items
        for record in data:
            price += (record.bundle_price*record.bundle_qty)
            val = {'product_id':record.product_name.id, 'price_unit':record.bundle_price,'product_uom_qty':record.bundle_qty,'original_qty':record.bundle_qty}
            sale_order_line.advance_bundle_order_lines = [(0,0,val)]
        if len(data) == 0:
            raise UserError(_("Please select atleast one product from bundle(s)"))
        else:
            sale_order_line.price_unit = price




    @api.onchange('advance_product_id')
    def get_bundle_items(self):
        _domain = []
        advance_product_items_ids = []
        product_selected = []
        for record in self.advance_product_id.advance_bundle_line_ids:
            _domain+=record.bundle_line_ids.ids
            if record._type == "required":     
                advance_product_items_ids =  record.bundle_line_ids.ids
            if record._type == "radio":
                product_selected = record.bundle_line_ids.ids
            if len(product_selected) > 0:
                advance_product_items_ids.append(product_selected[-1])
        
        self.advanced_product_items = [(6,0,advance_product_items_ids)]

        return {'domain':{'advanced_product_items':[('id','in',_domain)]}}
