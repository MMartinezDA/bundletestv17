import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

patch(PosStore.prototype, {
    async setup() {
        await super.setup(...arguments);
    },
    async _processData(loadedData) {
        await super._processData(...arguments);
        this._loadAdvanceBundleLines(loadedData["advance.bundle.lines"])
        this._loadAdvanceBundleProductItems(loadedData["advance.bundle.product.items"])
        this._loadProductProduct(loadedData['product.product']);
        this._loadAdvanceBundleOrderLine(loadedData["advance.bundle.order.line"])
    },
    _loadAdvanceBundleLines(lines) {
        var self = this;
        self.db.bundle_lines = lines
        self.db.bundle_lines_by_id = {};
        self.db.bundle_lines.forEach((line)=>self.db.bundle_lines_by_id[line.id] = line)
    },
    _loadAdvanceBundleProductItems(lines) {
        var self = this;
        self.db.bundle_product_items = lines
        self.db.bundle_product_items_by_id = {};
        self.db.bundle_product_items.forEach((line)=>self.db.bundle_product_items_by_id[line.id] = line)
    },
    _loadAdvanceBundleOrderLine(lines) {
        var self = this;
        self.db.bundle_order_line = lines
        self.db.bundle_orderline_by_id = {};
        self.db.bundle_order_line.forEach((line)=>self.db.bundle_orderline_by_id[line.id] = line)
    },

})