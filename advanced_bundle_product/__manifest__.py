# -*- coding: utf-8 -*-

{
    "name":  "Odoo Website Advanced Bundle Product",
    "summary":  """The customized shop page for selling product as a bundle with different options""",
    "category":  "Ecommerce",
    "version":  "17.0.0.0",
    "author":  "Datanalisis Consultores S.L.",
    "license":  "Other proprietary",
    "website":  "https://www.datanalisis.es",
    "description":  """The Customized shop page with bundle product that can be purchased together""",
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
