# -*- coding: utf-8 -*-

{
    "name"          :"POS Advanced Bundle Product",
    "summary"       :"""Customize products as a bundle with different options in POS.POS Advanced Bundle Product|Bundle Product POS|POS Advanced Bundle""",
    "version"       :"17.0.0",
    "author"        :"Datanalisis Consultores S.L.",
    "license"       :"Other proprietary",
    "website"       :"https://www.datanalisis.es/",
    "description"   : """Bundle product that can be purchased together in POS""",
    "depends"       : [
                        'point_of_sale',
                        'sale_management',
                        'advanced_bundle_product',
                      
                      ],
    "data"          : [
                        'security/ir.model.access.csv',
                        'views/bundle.xml',   
                      ],
    "demo"          :['demo/demo.xml'],
    "assets"        : {
                        'point_of_sale._assets_pos': [
                            'pos_advanced_bundle_product/static/src/overrides/**/*',
                            'pos_advanced_bundle_product/static/src/app/**/*',
                            'pos_advanced_bundle_product/static/src/css/**/*'
                        ],
                      },
    "images"        :  ['static/description/banner.gif'],
    "auto_install"  :False,
    "application"   :True,
    "installable"   :True,
    "price"         :  79,
    "currency"      :  "USD",
    "pre_init_hook" : "pre_init_check",
}
