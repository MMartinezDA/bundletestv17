/** @odoo-module */
/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

import { Order,Orderline } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import { BundleProductPopupWidget } from "@pos_advanced_bundle_product/app/popup/bundle_product_popup";

patch(Order.prototype, {
    setup(_defaultObj, options) {
        super.setup(...arguments);
    },

    async add_product(product, options) {
        var self = this;
        super.add_product(...arguments); 

        var updated_last_orderline = self.get_last_orderline() || {};
        var prod_name = product.display_name;
        var bundle_id = product.advance_bundle_line_ids;
        var bundle = self.pos.db.bundle_lines;
        var bundle_items = self.pos.db.bundle_product_items;
        var selected_bundle = []
        
        if (product && product.is_advance_bundle) {
            if (bundle) {
                for (var i = 0; i < bundle.length; i++) {   
                    if (bundle_id.find(o => o === bundle[i].id))
                        selected_bundle.push(bundle[i])
                }
            }
            var product_lines = []
            if (bundle_items) {
                for (var i = 0; i < bundle_items.length; i++) {
                    for (var j = 0; j < selected_bundle.length; j++) {
                        if (selected_bundle[j].bundle_line_ids.find(o => o === bundle_items[i].id))
                            product_lines.push(bundle_items[i])
                    }
                }
            }
            
        
            self.pos.popup.add( BundleProductPopupWidget , {
                'title': prod_name + " Products",
                'bundle_product_line': selected_bundle,
                'bundle_items': product_lines,
                'product': product,
                'orderline': updated_last_orderline,
                'checked_list': [],
                'bundle_quantity_dict': {},
            })
        }
    }
})

patch(Orderline.prototype, {
    setup(_defaultObj, options) {
        super.setup(...arguments);
        var self = this;
        self.bundle_checked_list = [];
        self.bundle_quantity_dict = {};
        self.product_arr = [];
        self.bundle_checked_product = [];
        self.selected_props_line = [];
        self.checked_prod_quant = {};
        self.all_prod_id = {};
        self.sel_products = [];
        if (options.json)
            self.sel_products = options.json.sel_products;
    },
    set_unit_price(price) {
        if (this.package_id) {
            
            this.order.assert_editable();
            var parsed_price = !isNaN(price) ?
                price :
                isNaN(parseFloat(price)) ? 0 : field_utils.parse.float('' + price)
            this.price = round_di(parsed_price || 0, 4);
            this.trigger('change', this);
        } else {
            super.set_unit_price(price)
        }
    },
    get_unit_display_price() {
        if (this.package_id) {
            return this.get_unit_price();
        } else {
            return super.get_unit_display_price(...arguments)
        }
    },
    get_unit_price() {
        if (this.package_id) {
            return parseFloat(round_di(this.price || 0, 4).toFixed(4));
        } else {
            return super.get_unit_price(...arguments)
        }
    },
    wk_check_bundle() {
        var self = this;
        if (!self.product.is_advance_bundle) {
            return false
        } else {
            return true;
        }
    },
    get_checked_lines() {
        var self = this;
        return self.sel_products;
    },
    export_as_JSON() {
        var self = this;
        var loaded = super.export_as_JSON(...arguments);
        loaded.bundle_lines = self.pos.bundle_lines;
        loaded.bundle_product_items = self.pos.bundle_product_items;
        loaded.bundle_order_line = self.pos.bundle_order_line;
        loaded.bundle_checked_list = self.bundle_checked_list;
        loaded.bundle_quantity_dict = self.bundle_quantity_dict;
        loaded.selected_props_line = self.selected_props_line;
        loaded.bundle_checked_product = self.bundle_checked_product;
        loaded.product_arr = self.product_arr;
        loaded.all_prod_id = self.all_prod_id;
        loaded.sel_products = self.sel_products;
        return loaded;
    },
    open_bundle_popup(event) {
        
        
        var orderline = this.props.line.orderline
        var prod_name = orderline.product.display_name;
        var self = this;
        var bundle_id = orderline.product.advance_bundle_line_ids;
        
        var bundle = orderline.pos.db.bundle_lines;
        var bundle_items = orderline.pos.db.bundle_product_items;
        
        var selected_bundle_line = [];
        if (bundle) {
            for (var i = 0; i < bundle.length; i++) {
                if (bundle_id.find(o => o === bundle[i].id))
                    selected_bundle_line.push(bundle[i])
            }
        }
        var product_order_lines = []
        if (bundle_items) {
            for (var i = 0; i < bundle_items.length; i++) {
                for (var j = 0; j < selected_bundle_line.length; j++)
                    if (selected_bundle_line[j].bundle_line_ids.find(o => o === bundle_items[i].id))
                        product_order_lines.push(bundle_items[i])
            }
        }
        self.env.services.pos.popup.add( BundleProductPopupWidget, {
            'title': prod_name + " Products",
            'bundle_product_line': selected_bundle_line,
            'bundle_items': product_order_lines,
            'product': orderline.product,
            'pos': self.pos,
            'orderline': orderline,
            'checked_list': orderline.bundle_checked_list,
            'bundle_quantity_dict': orderline.bundle_quantity_dict,
        })
    },

    getDisplayData() {
        var self = this;
        return {
            ...super.getDisplayData(),
            all_prod_id:self.all_prod_id,
            bundle_lines:self.pos.bundle_lines,
            bundle_product_items:self.pos.bundle_product_items,
            bundle_order_line:self.pos.bundle_order_line,
            bundle_checked_list:self.bundle_checked_list,
            sel_products:self.sel_products,
            bundle_checked_product:self.bundle_checked_product,
            get_checked :self.get_checked_lines(),
            open_bundle_popup: self.open_bundle_popup,
            wk_check_bundle:self.wk_check_bundle,
            product: self.product,
            get_unit : self.get_unit(),
            orderline : self,
        };
    },
    init_from_JSON(json) {
        var pack_lot_ids = [];
        if (this.has_product_lot) {
            this.pack_lot_lines.each(_.bind(function (item) {
                return pack_lot_ids.push([0, 0, item.export_as_JSON()]);
            }, this));
        }
        if (json && !json.pack_lot_ids)
            json.pack_lot_ids = pack_lot_ids
        
        super.init_from_JSON(json);
        if (json) {
            this.bundle_lines = json.bundle_lines;
            this.bundle_product_items = json.bundle_product_items;
            this.bundle_order_line = json.bundle_order_line;
            this.selected_props_line = json.selected_props_line;
            this.product_arr = json.product_arr;
            this.bundle_checked_product = json.bundle_checked_product;
            this.all_prod_id = json.all_prod_id;
            this.bundle_checked_list = json.bundle_checked_list;
            this.sel_products = json.sel_products;
            this.checked_prSuperOrderod_quant = json.checked_prod_quant;
            this.bundle_quantity_dict = json.bundle_quantity_dict;
        }
    },
})

