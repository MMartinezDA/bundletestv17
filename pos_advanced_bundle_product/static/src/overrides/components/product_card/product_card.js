/** @odoo-module */
/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

import { ProductCard } from "@point_of_sale/app/generic_components/product_card/product_card";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { patch } from "@web/core/utils/patch";

patch(ProductCard.prototype, {
    setup() {
        super.setup();
        this.pos = usePos();
    },
    wk_is_bundle_product(product_id) {
        var bundle_product = Object.values(this.pos.db.product_by_id);
        var adv_prod_item = bundle_product.filter(function (num) {
            return num.is_advance_bundle == true;
        });

        for (var i = 0; i < adv_prod_item.length; i++) {
            if (adv_prod_item[i].id == product_id) {
                return true;
            }
        }
    }
});