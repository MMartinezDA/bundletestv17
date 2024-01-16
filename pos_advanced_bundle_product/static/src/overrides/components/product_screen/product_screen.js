/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";


patch(ProductScreen.prototype, {
    setup() {
        super.setup(...arguments);
    },
    _setValue(val) {
        var self = this;
        var pos = this.pos;
        var curr_orderline = this.currentOrder.get_selected_orderline();
        if(curr_orderline){
            var adv_line = curr_orderline.product.is_advance_bundle;
            if (pos.numpadMode === 'quantity') {
                if (!adv_line) {
                    super._setValue(val)
                } else {
                    if (val != 'remove') {
                        curr_orderline.input_quantity = val
                        curr_orderline.set_quantity(val)
                        curr_orderline.set_unit_price(curr_orderline.final_price);
                    } else {
                        this.currentOrder.removeOrderline(curr_orderline)
                    }
                }
            } else if (pos.numpadMode === 'price') {
                if (!adv_line) {
                    super._setValue(val);
                } else {
                    self.popup.add(ErrorPopup, {
                        title: _t('Not Allowed'),
                        body: _t("You cannot change price of a Bundle Product."),
                    });
                }
            } else {
                super._setValue(val);
            }
        }
    },

})
