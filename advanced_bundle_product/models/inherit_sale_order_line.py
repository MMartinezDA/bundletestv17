from odoo import models, fields, api
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)



class inheritSaleOrderLine(models.Model):
    _inherit = "sale.order.line"


    def _get_display_price(self):
        self.ensure_one()
        if not self.product_id.is_advance_bundle:
            return super()._get_display_price()
        else:
            advance_bundle_product_items = self.advance_bundle_order_lines
            from_currency = self.product_id.bundle_product_currency_id if self.product_id.bundle_product_currency_id else self.product_id.currency_id
            for bundle_line in advance_bundle_product_items:
                product_price = from_currency._convert(bundle_line.price_unit,self.currency_id,self.company_id,datetime.today(),round=False)
                bundle_line.update({'price_unit':product_price})
            self.product_id.bundle_product_currency_id = self.currency_id
            return from_currency._convert(self.price_unit,self.currency_id,self.company_id,datetime.today())
        
    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        if self._context.get("skip_procurement"):
            return True
        

        non_bundle_lines = self.filtered(lambda line: not line.product_id.is_advance_bundle)

        return super()._action_launch_stock_rule(previous_product_uom_qty)
        
class InheritSaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        line_list = []
        order_bundle_lines = self.order_line.filtered(lambda line: line.advance_bundle_order_lines)
        for line in order_bundle_lines:
            for bundle_line in line.advance_bundle_order_lines:
                val = {'bundle_name':line.name,'product_id':bundle_line.product_id.id, 'price_unit':bundle_line.original_price,'product_uom_qty': bundle_line.product_uom_qty}
                line_list.append((0,0,val))
            line.unlink()
        self.order_line = line_list
        self._cr.commit()
        return super().action_confirm()

