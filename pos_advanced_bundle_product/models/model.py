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
import datetime
import logging
from itertools import groupby
import json
import ast

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit='stock.picking'
    def _create_move_from_pos_order_lines(self, lines):
        self.ensure_one()
        lines_by_product = groupby(sorted(lines, key=lambda l: l.product_id.id), key=lambda l: l.product_id.id)
        for product, lines in lines_by_product:
            order_lines = self.env['pos.order.line'].concat(*lines)
            first_line = order_lines[0]
            # -------- Picking for Product Bundle Items ---------
            if order_lines and order_lines.product_id.is_advance_bundle:
                for r in order_lines:
                    cached_json = ast.literal_eval(r.all_prod_id)
                    for wk_bundle_product in r.sel_products.filtered(lambda l: l.product_name.type in ['product', 'consu']):
                        if(wk_bundle_product in r.sel_products):
                            tot_qty =[] 
                            tot_qty.append(wk_bundle_product.bundle_qty)
                        if (str(wk_bundle_product.id) in cached_json.keys()):
                            qty_curr = cached_json[str(wk_bundle_product.id)]
                            tot =sum(r.mapped('qty'))
                            current_move = self.env['stock.move'].create(
                                        {
                                        'name': wk_bundle_product.display_name,
                                        'product_uom': wk_bundle_product.product_name.uom_id.id,
                                        'picking_id': self.id,
                                        'picking_type_id': self.picking_type_id.id,
                                        'product_id': wk_bundle_product.product_name.id,
                                        'product_uom_qty': float(qty_curr) * tot,
                                        'state': 'draft',
                                        'location_id': self.location_id.id,
                                        'location_dest_id': self.location_dest_id.id,
                                        'company_id': self.company_id.id,
                                    }
                                )

                            confirmed_moves = current_move._action_confirm()
                            for move in confirmed_moves:
                                move.quantity_done = move.product_uom_qty
                        else:
                            val = abs(sum(r.mapped('qty')))
                            current_move = self.env['stock.move'].create(
                                        {
                                        'name': wk_bundle_product.display_name,
                                        'product_uom': wk_bundle_product.product_name.uom_id.id,
                                        'picking_id': self.id,
                                        'picking_type_id': self.picking_type_id.id,
                                        'product_id': wk_bundle_product.product_name.id,
                                        'product_uom_qty':wk_bundle_product.bundle_qty *val ,
                                        'state': 'draft',
                                        'location_id': self.location_id.id,
                                        'location_dest_id': self.location_dest_id.id,
                                        'company_id': self.company_id.id,
                                    }
                                )
                            confirmed_moves = current_move._action_confirm()
                            for move in confirmed_moves:
                                move.quantity_done = move.product_uom_qty
            current_move = self.env['stock.move'].create(
                self._prepare_stock_move_vals(first_line, order_lines)
            )
            confirmed_moves = current_move._action_confirm()
            if not order_lines.product_id.is_advance_bundle: 
                for move in confirmed_moves:
                    if first_line.product_id == move.product_id and first_line.product_id.tracking != 'none':
                        if self.picking_type_id.use_existing_lots or self.picking_type_id.use_create_lots:
                            for line in order_lines:
                                sum_of_lots = 0
                                for lot in line.pack_lot_ids.filtered(lambda l: l.lot_name):
                                    if line.product_id.tracking == 'serial':
                                        qty = 1
                                    else:
                                        qty = abs(line.qty)
                                    ml_vals = move._prepare_move_line_vals()
                                    ml_vals.update({'qty_done':qty})
                                    if self.picking_type_id.use_existing_lots:
                                        existing_lot = self.env['stock.production.lot'].search([
                                            ('company_id', '=', self.company_id.id),
                                            ('product_id', '=', line.product_id.id),
                                            ('name', '=', lot.lot_name)
                                        ])
                                        if not existing_lot and self.picking_type_id.use_create_lots:
                                            existing_lot = self.env['stock.production.lot'].create({
                                                'company_id': self.company_id.id,
                                                'product_id': line.product_id.id,
                                                'name': lot.lot_name,
                                            })
                                        ml_vals.update({
                                            'lot_id': existing_lot.id,
                                        })
                                    else:
                                        ml_vals.update({
                                            'lot_name': lot.lot_name,
                                        })
                                    self.env['stock.move.line'].create(ml_vals)
                                    sum_of_lots += qty
                                if abs(line.qty) != sum_of_lots:
                                    difference_qty = abs(line.qty) - sum_of_lots
                                    ml_vals = current_move._prepare_move_line_vals()
                                    if line.product_id.tracking == 'serial':
                                        ml_vals.update({'qty_done': 1})
                                        for i in range(int(difference_qty)):
                                            self.env['stock.move.line'].create(ml_vals)
                                    else:
                                        ml_vals.update({'qty_done': difference_qty})
                                        self.env['stock.move.line'].create(ml_vals)
                        else:
                            move._action_assign()
                            sum_of_lots = 0
                            for move_line in move.move_line_ids:
                                move_line.qty_done = move_line.product_uom_qty
                                sum_of_lots += move_line.product_uom_qty
                            if float_compare(move.product_uom_qty, move.quantity_done, precision_rounding=move.product_uom.rounding) > 0:
                                remaining_qty = move.product_uom_qty - move.quantity_done
                                ml_vals = move._prepare_move_line_vals()
                                ml_vals.update({'qty_done':remaining_qty})
                                self.env['stock.move.line'].create(ml_vals)

                    else:
                        move.quantity_done = move.product_uom_qty

class PosOrderLine(models.Model):
    _inherit = "pos.order.line" 

    sel_products  = fields.Many2many("advance.bundle.product.items","line_bun_rel")
    all_prod_id  = fields.Text('Product Quantities')

    def _order_line_fields(self, line, session_id=None):
        res = super(PosOrderLine,self)._order_line_fields(line, session_id=None)
        prod_ids= []
        for i in line[2].get('sel_products',[]):
            prod_ids.append(i['id'])
        res[2].update({'sel_products': [(6, 0, prod_ids)] ,'all_prod_id':json.dumps(line[2].get('all_prod_id',""))})    
        return res

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        new_model_product_product = "product.product"
        if new_model_product_product not in result:
            result.append(new_model_product_product)
        new_model_advanced_bundle_lines = "advance.bundle.lines"
        if new_model_advanced_bundle_lines not in result:
            result.append(new_model_advanced_bundle_lines)
        new_model_advanced_bundle_product_items = "advance.bundle.product.items"
        if new_model_advanced_bundle_product_items not in result:
            result.append(new_model_advanced_bundle_product_items)
        new_model_advanced_bundle_order_line = "advance.bundle.order.line"
        if new_model_advanced_bundle_order_line not in result:
            result.append(new_model_advanced_bundle_order_line)
        return result

    def _loader_params_product_product(self):
        result = super()._loader_params_product_product()
        result['search_params']['fields'].extend(['is_advance_bundle','advance_bundle_line_ids'])
        return result

    def _loader_params_advance_bundle_lines(self):
        model_fields = ['_type', 'name', 'allow_none', 'pre_qty','bundle_line_ids','bundle_item','sequence']
        return {'search_params': {'domain': [], 'fields': model_fields}}

    def _get_pos_ui_advance_bundle_lines(self, params):
        return self.env["advance.bundle.lines"].search_read(**params['search_params'])

    def _loader_params_advance_bundle_product_items(self):
        model_fields = ['product_name', 'bundle_lines', 'bundle_qty', 'bundle_price','currency_id']
        return {'search_params': {'domain': [], 'fields': model_fields}}

    def _get_pos_ui_advance_bundle_product_items(self, params):
        return self.env["advance.bundle.product.items"].search_read(**params['search_params'])

    def _loader_params_advance_bundle_order_line(self):
        model_fields = ['product_id', 'advance_order_line', 'price_unit', 'product_uom_qty','product_image','original_qty','currecny_id']
        return {'search_params': {'domain': [], 'fields': model_fields}}

    def _get_pos_ui_advance_bundle_order_line(self, params):
        return self.env["advance.bundle.order.line"].search_read(**params['search_params'])