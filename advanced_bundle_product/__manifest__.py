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

{
    "name":  "Odoo Website Advanced Bundle Product",
    "summary":  """The customized shop page for selling product as a bundle with different options""",
    "category":  "Ecommerce",
    "version":  "1.0.0",
    "author":  "Webkul Software Pvt. Ltd.",
    "license":  "Other proprietary",
    "website":  "http://www.webkul.com",
    "description":  """The Customized shop page with bundle product that can be purchased together""",
    "live_test_url":  "http://odoodemo.webkul.com/?module=advanced_bundle_product&version=16.0&custom_url=/bundle/product",
    "depends":  [
        'sale_management',
        'website',
        'website_sale',
        'stock',
    ],
    "data":  [
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/bundle_order_lines.xml',
        'wizard/sale_order_wizard.xml',
        'views/sale_order_view.xml',
        'views/product_template.xml',
        'views/advance_bundle_product.xml',
    ],
    "demo":  ['demo/demo.xml'],
    "assets": {
        'web.assets_frontend': [
            "advanced_bundle_product/static/src/scss/main.scss",
            "advanced_bundle_product/static/src/js/main.js",
        ],
    },

    "images":  ['static/description/Banner.png'],
    "price":  "99",
    "currency":  "USD",
    "pre_init_hook": "pre_init_check",
}
