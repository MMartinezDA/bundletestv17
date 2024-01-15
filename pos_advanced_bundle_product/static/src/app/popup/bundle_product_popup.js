import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";

export class BundleProductPopupWidget extends AbstractAwaitablePopup {
    static template = "pos_advanced_bundle_product.BundleProductPopupWidget";
    static defaultProps = {
        confirmText: _t("Ok"),
        title: _t("Error"),
        cancelKey: false,
        sound: true,
    };
    setup() {
        super.setup();
        var self = this;
        self.options = self.props || {};
        self.quantity;
        self.total_price;
        self.unit_price;
        self.e;
    }
    
    click_cancel() {
        let { pos } = this.env.services;
        let curr_order = pos.get_order().get_selected_orderline()
        if (curr_order && !curr_order.bundle_checked_product.length) {
            pos.get_order().removeOrderline(curr_order)
        }
        this.cancel();
    }

    apply_bundle(e) {
        var self = this;
        var pos = self.env.services.pos;
        var props_line = self.props.bundle_product_line
        var orderline = self.props.orderline
        orderline.selected_props_line = props_line
        var total_price = [];
        var addon_arr = [];
        var addon_set = new Set()
        var product_arr = [];
        var prod_set;
        var checked_qty = {};
        var quantity_dict = {};
        var all_prod_id = {};
        var qty_addons = [];
        var radio_el = []
        if (props_line) {
            for (var i = 0; i < props_line.length; i++) {
                if (props_line[i]._type == "requiredopt") {
                    if ($('.requiredopt_main').prop('checked')) {
                        $(".requiredopt_bundle").each(function () {
                            $('.requiredopt_bundle').prop('checked', true)
                            var qty = $(this).closest("td").siblings(".qty").html()
                            var price = $(this).closest("td").siblings(".product_price").html()
                            total_price.push((qty) * price)
                        })
                    } else {
                        $(".requiredopt_bundle").each(function () {
                            $('.requiredopt_bundle').prop('checked', false)
                        })
                    }
                }
                else if (props_line[i]._type == "optional") {
                    $('.optional_bundle').each(function () {
                        if ($(this).prop('checked')) {
                            var qty = $("input.optional_bundle").closest("td").siblings(".qty").html()
                            checked_qty[$('.optional_bundle').attr('product_id')] = qty
                            product_arr = product_arr.concat(props_line[i].bundle_line_ids)
                            prod_set = new Set(product_arr)
                            product_arr = Array.from(prod_set)
                            var price = $(this).closest("td").siblings(".product_price").html()
                            total_price.push(qty * price);
                        }
                    })
                }
                else if (props_line[i]._type == "accessories" || props_line[i]._type == "addon") {
                    $('.addon_bundle').each(function () {
                        if ($(this).prop('checked')) {
                            $('.addon_quantity').each(function (idx, element) {
                                var qty_add = $(element).val()
                                qty_addons.push(qty_add)
                                var prod_id = $(element).attr('product_id')
                                all_prod_id[prod_id] = qty_add
                            })
                            prod_set = new Set(product_arr)
                            product_arr = Array.from(prod_set)
                            var all_checked_quant = $('.addon_bundle:checked');
                            var qty = $(this).closest(".add_advance_product").find(".qty  input").val();
                            var price = $(this).closest("td").siblings(".product_price").html();
                            addon_set.add(qty * price);
                            all_checked_quant.each(function (idx, element) {
                                var qty_new = $(this).closest(".add_advance_product").find(".qty  input").val();
                                if (all_checked_quant[idx] !== undefined) {
                                    quantity_dict[$(element).attr('id')] = qty_new;
                                }
                            })
                            product_arr = product_arr.concat(props_line[i].bundle_line_ids)
                            addon_arr = Array.from(addon_set);
                        }
                    })
                }
                else if (props_line[i]._type == "radio") {
                    $('.radio_bundle:checked').each(function (index, el) {
                        var qty = $(el).closest("td").siblings(".qty").html();
                        var price = $(el).closest("td").siblings(".product_price").html();
                        radio_el.push(qty * price);
                        radio_el = radio_el.splice(0, $('.radio_bundle:checked').length);
                        checked_qty[$(el).attr('product_id')] = qty;
                        total_price = radio_el;
                    })
                }
                else if (props_line[i]._type == "required") {
                    var tot_qty = []
                    $('.req_qty').each(function (idx, element) {
                        var qty = $(element).html()
                        checked_qty[$('.required_bundle').attr('product_id')] = qty
                        tot_qty.push(qty)
                    })
                    var tot_price = [];
                    $(".req_product_price").each(function (idx, element) {
                        var price = $(element).html()
                        tot_price.push(price)
                    })
                    for (var val = 0; val < tot_price.length; val++) {
                        total_price.push(tot_qty[val] * tot_price[val])
                    }
                }
            }
        }

        if (self.props.orderline) {
            var line = self.props.orderline;
            var final_price = 0;
            var sum_bundles = total_price.concat(addon_arr).reduce((a, b) => a + b, 0)
            final_price = sum_bundles;
            line.set_unit_price(final_price);
            line.final_price = final_price;
            line.price_manually_set = true;
        }
        var checked_list = [];
        var checked_product = [];
        var checked_prod_quant = {}
        var all_checked_items = $('.static_input:checked');
        all_checked_items.each(function (idx, element) {
            checked_list.push($(element).attr('id'))
            checked_product.push($(element).attr('product_id'))
        })
    
        orderline.bundle_checked_list = checked_list;
        orderline.bundle_quantity_dict = quantity_dict;
        orderline.bundle_checked_product = checked_product;
        orderline.product_arr = product_arr;
        orderline.checked_prod_quant = checked_prod_quant;
        orderline.all_prod_id = all_prod_id;
        var items = pos.db.bundle_product_items;
        var bundle_sel_products = []
        if (items) {
            for (var i = 0; i < items.length; i++) {
                if (checked_product.find(o => o == items[i].id)) {
                    bundle_sel_products.push(items[i])
                }
            }
        }
        orderline.sel_products = bundle_sel_products;
        
        var order = pos.get_order();
        order.save_to_db();
        self.cancel()
    }
}