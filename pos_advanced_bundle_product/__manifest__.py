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
    "name"          :"POS Advanced Bundle Product",
    "summary"       :"""Customize products as a bundle with different options in POS.POS Advanced Bundle Product|Bundle Product POS|POS Advanced Bundle""",
    "version"       :"1.0.2",
    "author"        :"Webkul Software Pvt. Ltd.",
    "license"       :"Other proprietary",
    "website"       :"http://www.webkul.com",
    "description"   : """Bundle product that can be purchased together in POS""",
    "live_test_url" : "http://odoodemo.webkul.com/?module=pos_advanced_bundle_product&custom_url=/pos/web",
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
