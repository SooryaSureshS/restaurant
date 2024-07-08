odoo.define("website_product_bulk_orders.new_order_popup", function (require) {

    var publicWidget = require('web.public.widget');
    var rpc = require('web.rpc');
    var core = require('web.core');

    publicWidget.registry.newOrderPopup = publicWidget.Widget.extend({
        selector: '.new_order_popup',
        events: {
            'click #new_order_button': '_onNewOrderButtonClick',
            'click button.model_bulk_add_to_cart': '_onBulkAddToCartClick',
            'click a.model_bulk_add_to_cart': '_onBulkAddToCartClick',
            'keyup input.product_variant_qty': '_onQtyChange',
             'click.product_variant_qty': '_onQtyChange',
        },

        init: function () {
            this._super.apply(this, arguments);
            this.temp_val = ''
        },

        _onQtyChange: function (ev) {
            var colorId = $(ev.target).attr('data-color-id');
            var pid = $(ev.target).attr('data-ptl');
            var qty = 0;
            var tot = 0;
            $('.input-'+pid+'-'+colorId).each(function () {
                if ($(this).val()){
                    qty += parseFloat($(this).val());
                    tot += parseFloat($(this).attr('data-unit_price'))*parseFloat($(this).val());
                }
            })
            $('#qty-'+pid+'-'+colorId).text(qty);
            $('#price-'+pid+'-'+colorId).text(tot);
        },
        _onNewOrderButtonClick: function (ev) {
            var self = this;
            var selectTemplateModels = $('#myModal').find('select#product_tmpl_id');
            var domiain = [['type', '=', 'product'], ['website_published', '=', true]]
            if (parseInt($(ev.currentTarget).data('product_id'))) {
                domiain.push([
                    'id', '=', parseInt($(ev.currentTarget).data('product_id'))
                ])
            }

            this._rpc({
                route: '/get/product/template/data',
                params: {
                'id':parseInt($(ev.currentTarget).data('product_id'))
                }
            }).then(function (records) {
                if (records.length) {
                    $(selectTemplateModels).empty()
                    _.each(records, function (x) {
                        var opt = $('<option>').text(x['name']).attr('value', x['id']);
                        selectTemplateModels.append(opt);
                    });
                    var productTemplate = records[0];
                    self.temp_val = productTemplate['id']
                    self.updateModelBodyVariants(productTemplate['id'])
                }
            })
//            rpc.query({
//                model: 'product.template',
//                method: 'search_read',
//                args: [domiain, ['name', 'product_variant_ids']],
//            }).then(function (records) {
//                if (records.length) {
//                    $(selectTemplateModels).empty()
//                    _.each(records, function (x) {
//                        var opt = $('<option>').text(x['name']).attr('value', x['id']);
//                        selectTemplateModels.append(opt);
//                    });
//                    var productTemplate = records[0];
//                    self.temp_val = productTemplate['id']
//                    self.updateModelBodyVariants(productTemplate['id'])
//                }
//            });
        },

        updateModelBodyVariants: function (productTemplateId) {
            this._rpc({
                route: '/get/all/product/data',
                params: {
                    'id':productTemplateId
                }
            }).then(function (productData) {

                var $modelBody = $('#myModal').find('.modal-body');
                $modelBody.find('tbody').html('');
                $modelBody.find('thead').html('');
                $modelBody.find('tbody').get(0).scrollIntoView();

                var sizeText = ''
                _.each(productData['size'], function (x) {
                    sizeText += '<td style="text-align:center;\n' +
                        '        position: sticky;\n' +
                        '        top: 0;    box-shadow: inset 1px 1px #DEE2E6, 0 1px #DEE2E6;border: 0px solid #DEE2E6;background-color: white;">' + x[1] + '</td>'
                })

                $("#variantTable").find('thead')
                    .append($('<tr>')
                        .append($('<th width="15%" style="\n' +
                            '        position: sticky;\n' +
                            '        top: 0;    box-shadow: inset 1px 1px #DEE2E6, 0 1px #DEE2E6;border: 0px solid #DEE2E6;background-color: white;"></th>'))
                        .append(sizeText)
                    );

                _.each(productData['color'], function (y) {
                    var sizeText = ''
                    _.each(productData['size'], function (x) {
                        var productId = productData['color_size_variant_mapping'][y[0] + '-' + x[0]][0]
                        var productStock = productData['color_size_variant_mapping'][y[0] + '-' + x[0]][2]
                        sizeText += '<td valign="middle" style="vertical-align: middle;"><input type="text" t-att-data-product-id="' + productId + '" t-att-data-size-id="' + x[0] + '" t-att-data-color-id="' + y[0] + '" class="form-control product_variant_qty"/><p style="margin: 0px; font-family: arial, sans-serif; font-weight: 400; font-size: 12px; color: #1a1a18; text-align:center;">' + productStock + ' in stock</p></td>'
                    })
                    var firstProductId = productData['color_size_variant_mapping'][y[0] + '-' + productData['size'][0][0]][0];
                    var firstProductPrice = productData['color_size_variant_mapping'][y[0] + '-' + productData['size'][0][0]][1];
                    var currencySymbol = productData['currency_symbol'];
                    img_txt = '<img src="/web/image/product.product/' + firstProductId + '/image_128" style="width: 64px; height: 64px; object-fit: contain;" alt="Product image"/>'
                    $("#variantTable").find('tbody')
                        .append($('<tr>')
                            .append($('<td width="15%" style="text-align:center">' + img_txt + '<p style="margin: 0px; font-family: arial, sans-serif; font-weight: 400; font-size: 16px; color: #1a1a18;">' + y[1] + '</p><p style="margin: 0px; opacity: 0.3; font-family: arial, sans-serif; font-weight: 400; font-size: 12px; color: #1a1a18;">' + firstProductPrice + ' ' + currencySymbol + ' VAT excl</p></td>'))
                            .append(sizeText)
                        );
                    $('#smart_loading').hide();
                    $('#myModal').modal('show');
                })
            })
           /* this._rpc({
                model: 'product.template',
                method: 'get_all_product_template_data',
                args: [[productTemplateId]]
            }).then(function (productData) {

                var $modelBody = $('#myModal').find('.modal-body');
                $modelBody.find('tbody').html('');
                $modelBody.find('thead').html('');
                $modelBody.find('tbody').get(0).scrollIntoView();

                var sizeText = ''
                _.each(productData['size'], function (x) {
                    sizeText += '<td style="text-align:center;\n' +
                        '        position: sticky;\n' +
                        '        top: 0;    box-shadow: inset 1px 1px #DEE2E6, 0 1px #DEE2E6;border: 0px solid #DEE2E6;background-color: white;">' + x[1] + '</td>'
                })

                $("#variantTable").find('thead')
                    .append($('<tr>')
                        .append($('<th width="15%" style="\n' +
                            '        position: sticky;\n' +
                            '        top: 0;    box-shadow: inset 1px 1px #DEE2E6, 0 1px #DEE2E6;border: 0px solid #DEE2E6;background-color: white;"></th>'))
                        .append(sizeText)
                    );

                _.each(productData['color'], function (y) {
                    var sizeText = ''
                    _.each(productData['size'], function (x) {
                        var productId = productData['color_size_variant_mapping'][y[0] + '-' + x[0]][0]
                        var productStock = productData['color_size_variant_mapping'][y[0] + '-' + x[0]][2]
                        sizeText += '<td valign="middle" style="vertical-align: middle;"><input type="text" t-att-data-product-id="' + productId + '" t-att-data-size-id="' + x[0] + '" t-att-data-color-id="' + y[0] + '" class="form-control product_variant_qty"/><p style="margin: 0px; font-family: arial, sans-serif; font-weight: 400; font-size: 12px; color: #1a1a18; text-align:center;">' + productStock + ' in stock</p></td>'
                    })
                    var firstProductId = productData['color_size_variant_mapping'][y[0] + '-' + productData['size'][0][0]][0];
                    var firstProductPrice = productData['color_size_variant_mapping'][y[0] + '-' + productData['size'][0][0]][1];
                    var currencySymbol = productData['currency_symbol'];
                    img_txt = '<img src="/web/image/product.product/' + firstProductId + '/image_128" style="width: 64px; height: 64px; object-fit: contain;" alt="Product image"/>'
                    $("#variantTable").find('tbody')
                        .append($('<tr>')
                            .append($('<td width="15%" style="text-align:center">' + img_txt + '<p style="margin: 0px; font-family: arial, sans-serif; font-weight: 400; font-size: 16px; color: #1a1a18;">' + y[1] + '</p><p style="margin: 0px; opacity: 0.3; font-family: arial, sans-serif; font-weight: 400; font-size: 12px; color: #1a1a18;">' + firstProductPrice + ' ' + currencySymbol + ' VAT excl</p></td>'))
                            .append(sizeText)
                        );
                    $('#smart_loading').hide();
                    $('#myModal').modal('show');
                })

            });*/
        },

        _onBulkAddToCartClick: function (ev) {
            var $variantInputs = $('.new_order_popup').find('input.product_variant_qty');
            var update_cart_product_ids = {}
            _.each($variantInputs, function (inputBox) {
//                if ($(inputBox).val() !== '' && parseInt($(inputBox).val()) > 0) {
                    update_cart_product_ids[$(inputBox).attr('data-product-id')] = $(inputBox).val();
//                }

            });
            this._rpc({
                route: '/shop/cart/new_order_bulk_update',
                params: update_cart_product_ids
            }).then(function (result) {
                return window.location.href = "/shop/confirm_order";
            })
        }

    });

    publicWidget.registry.cartLine = publicWidget.Widget.extend({
        selector: '.newCartLine',
        events: {
            'click .expand': 'expandClick',
            'click .shrink': 'shrinkClick',
            'click .js_delete_product_group': 'deleteProductGroup',
        },

        init: function () {
            this._super.apply(this, arguments);
            $('.shrink').each(function(){
                $(this).hide();
            });
            $('.subline').each(function(){
                $(this).hide();
            });
        },

        start: function () {
            this._super.apply(this, arguments);
            $('.shrink').each(function(){
                $(this).hide();
            });
            $('.subline').each(function(){
                $(this).hide();
            });
        },
        deleteProductGroup: function (e) {
            this._rpc({
                route: '/shop/cart/deleteProductGroup',
                params: {prod_tmpl: e.currentTarget.getAttribute('data-prod_tmpl')}
            }).then(function (result) {
                return window.location.href = "/shop/cart";
            })
        },
        expandClick: function (e) {
            var class_name = e.currentTarget.value;
            $('.expand_'+class_name).hide();
            $('.shrink_'+class_name).show();
            $('.subline_'+class_name).each(function(){
                $(this).show();
            });
        },
        shrinkClick: function (e) {
            var class_name = e.currentTarget.value;
            $('.shrink_'+class_name).hide();
            $('.expand_'+class_name).show();
            $('.subline_'+class_name).each(function(){
                $(this).hide();
            });
        },
    });

});
