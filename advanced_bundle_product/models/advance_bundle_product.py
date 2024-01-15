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


from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class ProductProdcutCustom(models.Model):
    _inherit = "product.product"
    in_bundle = fields.Boolean('In Bundle')


class AdvanceBundleProductItems(models.Model):
    _name = "advance.bundle.product.items"
    _rec_name = "product_name"
    _description = "Advance Bundle Product Items"

    product_name = fields.Many2one('product.product','Select Product', required=True)
    bundle_lines = fields.Many2one('advance.bundle.lines','Bundle Lines')
    bundle_qty = fields.Integer('Bundle Quantity',default="1",required=True)
    bundle_price = fields.Float('Price',required=True)
    currency_id = fields.Many2one("res.currency",related="product_name.currency_id")

    @api.onchange('product_name')
    def _change_price(self):
        if self.product_name:
            self.bundle_price = self.product_name.lst_price
        domain = {'domain':{'product_name':[('is_published','=',True)]}}
        return domain
    
    @api.model
    def unlink(self):
        for adv_product in self:
            adv_product.product_name.in_bundle = False
        res = super().unlink()
        return res
    
    @api.model
    def create(self, vals):
        record = super(AdvanceBundleProductItems, self).create(vals)
        for adv_prodcut in record:
            adv_prodcut.product_name.in_bundle = True
        return record
    

class AdvanceBundleLines(models.Model):
    _name = "advance.bundle.lines"
    _order = "sequence asc"
    _description = "Advance Bundle Lines"

    _type = fields.Selection([('radio','Radio'),('required','Required'),('optional','Optional'),('requiredopt','Required(Optional)'),('addon','Add-On'),('accessories','Accessories')],required=True)
    name = fields.Char('Name',required=True)
    allow_none = fields.Boolean(string='Allow None')
    pre_qty = fields.Boolean(string='Preset Quantity')
    bundle_line_ids = fields.One2many('advance.bundle.product.items',inverse_name='bundle_lines')
    bundle_item = fields.Many2one('product.template','Bundle Item')
    sequence = fields.Char(string="Sequence", copy=False, default='1')

    @api.model
    def create(self, vals):
        if not vals.get('bundle_line_ids',False):
            raise UserError(_("Please select atleast one product in bundle section product"))

        if vals.get('sequence', 'New') == 'New':
            vals['sequence'] = self.env['ir.sequence'].next_by_code('self.sequence') or 'New'
        record_sequence = super().create(vals)
        return record_sequence
    
    @api.model
    def unlink(self):
        for bundle in self:
            for adv_prodcut in bundle.bundle_line_ids:
                adv_prodcut.product_name.in_bundle = False
        res = super().unlink()
        return res
    