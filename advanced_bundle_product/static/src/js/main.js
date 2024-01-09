/** @odoo-module **/

import sAnimations from "@website/js/content/snippets.animation";
import { jsonrpc } from "@web/core/network/rpc_service";

function escapeRegExp(text) {
  return text.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, "\\$&");
}

function numberWithCommas(price, dec_point, thousands_sep, grouping) {
  price = parseFloat(price).toFixed(2);
  var array = price.toString().split(".");
  price = "";
  var lastDigit = array[array.length - 1];
  var firstDigit = array[0];
  
  var sparatorPosition = grouping;
  
  sparatorPosition = sparatorPosition[0];
  firstDigit = firstDigit.split("");
  var x = 0
  for (var i = firstDigit.length - 1; i >= 0; i--) {
  x++;
  if (x == sparatorPosition && i != 0) {
  x = 0;
  price = price.concat(firstDigit[i]).concat(thousands_sep);
  } else {
  price = price.concat(firstDigit[i]);
  }
  }
  price = price.split("").reverse().join("");
  price = price.concat(dec_point).concat(lastDigit);
  return price;
  };

sAnimations.registry.AdvancedBundle = sAnimations.Class.extend({
  selector: "#wrap",
  constraints: null,
  events: {
    "click #advanced_add_to_cart": "_CreateSaleOrderLine",
    "change #required_optional": "_SelectRequiredOptional",
    "click .toggle_bundle": "_toggleContent",
    "change #advacned_bundle_details .static_input": "_CalculateProductPrice",
    "change #advacned_bundle_details .dynamic_input":
      "_CalculateProductPrice",
    "change #advacned_bundle_details #required_optional":
      "_CalculateProductPrice",
    "change #advacned_bundle_details .qty input": "_CalculateProductPrice",
    "click .bundle_collapse": "_ToggleUpDown",
  },
  start: function () {
    var self = this;
    var code = $("html").attr("lang");
    try {
      jsonrpc("/website/wk_lang", {
          code: code,
        })
        .then(function (res) {
          self.constraints = res;
          self._CalculateProductPrice();
        });
    } catch (e) {
      console.error(e);
    }
  },

  _ToggleUpDown: function (ev) {
    $(ev.currentTarget).toggleClass("icon_up icon_down");
    $(ev.currentTarget)
      .closest(".wk_advanced_table")
      .find("tbody")
      .fadeToggle();
  },

  _CreateSaleOrderLine: function (ev) {
    var data = [];
    var main_product = parseInt($("#advanced_bundle .product_id").val());
    var bundle_products = $(
      "#advacned_bundle_details .add_advance_product .static_input:checked"
    )
    var main_product_qty = parseInt(
      $("#advance_bundle_quantity input").val()
    );
    if (!main_product_qty | parseInt(main_product_qty)<=0){
      $('#advance_bundle_modal').modal('show');
      return 
    }
    if (!bundle_products.length){
      var modal = $('#advance_bundle_modal')
      modal.find('.modal-body').text('Atlease one bundle product should be selected.')
      modal.modal('show');
      return
    }
    data.push([main_product, main_product_qty, 0]);

    var thousand_sep = new RegExp(
      escapeRegExp(this.constraints.thousands_sep),
      "g"
    );
    var decimal_sep = new RegExp(
      escapeRegExp(this.constraints.decimal_point),
      "g"
    );
    
    bundle_products.each(function () {
      if ($(this).hasClass("dynamic_field")) {
        var _id = parseInt($(this).val());
        var qty = parseInt(
          $(this).closest(".add_advance_product").find(".qty input").val()
        );

        var bundle_price = parseFloat(
          $(this)
            .closest(".add_advance_product")
            .find(".advanced_product_price .wk_adv_price span")
            .text()
            .replace(thousand_sep, "")
            .replace(decimal_sep, ".")
        );
        data.push([_id, qty, bundle_price]);
      } else {
        var _id = parseInt($(this).val());
        var qty = parseInt(
          $(this).closest(".add_advance_product").find(".qty").text()
        );

        var bundle_price = parseFloat(
          $(this)
            .closest(".add_advance_product")
            .find(".advanced_product_price .wk_adv_price span")
            .text()
            .replace(thousand_sep, "")
            .replace(decimal_sep, ".")
        );
        data.push([_id, qty, bundle_price]);
      }
    });
    var total_price = parseFloat(
      $(".wk_advanced_bundle .oe_price_h4 b .oe_currency_value")
        .text()
        .replace(thousand_sep, "")
        .replace(decimal_sep, ".")
    );
    jsonrpc("/shop/bundle/product", {
        data: data,
        total_price: total_price,
      })
      .then(function () {
        window.location.href = "/shop/cart";
      });
  },

  _SelectRequiredOptional: function (ev) {
    var check = $("#required_optional").prop("checked");
    $(ev.currentTarget)
      .closest(".wk_advanced_table")
      .find(".add_advance_product input")
      .prop("checked", check);
  },

  _toggleContent: function (ev) {
    $(ev.currentTarget).find("i").toggleClass("fa-angle-right fa-angle-down");
    $(ev.currentTarget).closest(".table").find("tbody,thead").fadeToggle();
  },

  _CalculateProductPrice: function () {
    var total_price = 0;
    var thousand_sep = new RegExp(
      escapeRegExp(this.constraints.thousands_sep),
      "g"
    );
    var decimal_sep = new RegExp(
      escapeRegExp(this.constraints.decimal_point),
      "g"
    );
    var sep_format = this.constraints.sep_format;
    var dec_point = this.constraints.decimal_point;
    var thousand_point = this.constraints.thousands_sep;
    $(".static_input:checked").each(function () {
      var qty = 1;
      var original_qty = 1;
      var element = $(this)
        .closest(".add_advance_product")
        .find(".advanced_product_price");

      if ($(this).is("#none_radio")) {
        qty = 1;
        original_qty = 1;
        var price = 0;
        var original_price = 0;
      } else {
        if (element.hasClass("dynamic_input")) {
          qty = parseInt(
            element.closest(".add_advance_product").find(".qty input").val()
          );
          original_qty = parseInt(
            element
              .closest(".add_advance_product")
              .find(".qty input")
              .attr("data-original-qty")
          );
        } else {
          qty = parseInt(
            element.closest(".add_advance_product").find(".qty").text()
          );
          original_qty = parseInt(
            element
              .closest(".add_advance_product")
              .find(".qty")
              .attr("data-original-qty")
          );
        }
        var price = parseFloat(
          element
            .find(".wk_adv_price span")
            .text()
            .replace(thousand_sep, "")
            .replace(decimal_sep, ".")
        );
        var original_price = element
          .find(".wk_adv_price")
          .data("original-price");

        price = (original_price / original_qty) * qty;
        element
          .find(".wk_adv_price span")
          .text(
            numberWithCommas(
              price.toFixed(2),
              dec_point,
              thousand_point,
              sep_format
            )
          );
      }
      try {
        if (qty > 0) {
          total_price += price;
        } else {
          alert("Quantity cannot be zero or less than zero");
          element.closest(".add_advance_product").find(".qty input").val("1");
        }
      } catch (e) {
        alert("Quantity must be number and greater than 0");
      }
    });
    $("#advanced_bundle .oe_price_h4 b .oe_currency_value").text(
      numberWithCommas(
        total_price.toFixed(2),
        dec_point,
        thousand_point,
        sep_format
      )
    );
  },
});
