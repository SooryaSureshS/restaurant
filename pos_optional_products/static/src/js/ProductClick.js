odoo.define('pos_optional_products.ProductClick.js',function (require) {
    "use strict";


    const { parse } = require('web.field_utils');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const PosComponent = require('point_of_sale.PosComponent');
    const { useErrorHandlers } = require('point_of_sale.custom_hooks');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const { Gui } = require('point_of_sale.Gui');
    const { onChangeOrder } = require('point_of_sale.custom_hooks');
    var models = require('point_of_sale.models');
    var DB = require('point_of_sale.DB');
    var core = require('web.core');
    var _t = core._t;
    var rpc = require('web.rpc');
    models.load_fields("product.product", ['optional_product_ids','product_option_group','is_bundle_product','bundle_product_ids']);
    models.load_fields("options.group", ['sequence']);
    models.load_models({
        model: 'product.bundles',
        fields: [],
        loaded: function(self, bundle_products) {
            self.bundle_products = bundle_products;
        }
    });
    const ProductClick = (ProductScreen) =>
        class ProductScreens extends ProductScreen {
        constructor() {
            super(...arguments);
             useListener('mousedown', '.product', this.product_onlod);

        }

        product_onlod(event){
         var self=this;
            var pressTimer;
            self.env.pos.optional_products_large = [];
           $(".product").mouseup(function(){

              clearTimeout(pressTimer);
              // Clear timeout
            //  return false;
            }).mousedown(function(event){
              // Set timeout
              pressTimer = window.setTimeout(function() {

                    var parent_product = $(event.currentTarget).attr('data-product-id');
                    var parent_product_detail = self.env.pos.db.get_product_by_id(parent_product);
                     self.env.pos.optional_parent_product_large = parent_product_detail;
                    if(parent_product_detail.optional_product_ids[0]){
                       var optional_products = [];
                    rpc.query({
                        model: 'product.product',
                        method: 'get_product_full_details',
                        args: [parent_product_detail.optional_product_ids],
                    }).then(function (result) {
                        if (result.length>0){
                            for (var i=0;i<result.length; i++){
                                var data= self.env.pos.db.get_product_by_id(result[i]['id']);
                                if (data){
                                    data['option_sequence']=result[i].sequence;
                                }
                                optional_products.push(data);
                            }
                        }
                        self.env.pos.optional_products_large = optional_products;
//                    self.env.pos.optional_parent_product_large = parent_product_detail;
                    Gui.showPopup("OptionalProductsPopupLarge", {
                        title : _t("Optional Products"),
                        confirmText: _t("Exit")
                    });
                    });
                    }
                    else{
                    self.env.pos.optional_products_large = [];
                       Gui.showPopup("OptionalProductsPopupLarge", {
                        title : _t("Optional Products"),
                        confirmText: _t("Exit")
                    });
                    }

              },500);
              return false;
            });

        }

        mounted() {
            this.env.pos.on('change:selectedClient', this.render, this);





        }
        async _clickProduct(event) {
            if (!this.currentOrder) {
                this.env.pos.add_new_order();
            }
            const product = event.detail;
            var products = product.optional_product_ids;
            if (product.bundle_product_ids[0]){
                var bundle_products = []
                var self = this;
                rpc.query({
                        model: 'product.product',
                        method: 'get_bundle_product',
                        args: [product.id],
                    }).then(function (result) {
//                        console.log("====", result)
//                        self.bundle_product_product_data = result;
                        for (var i=0;i<result.length; i++){
                            bundle_products.push(data);
                        }
                        self.env.pos.bundle_total_count= result['total_count'];
//                        console.log("self.env.pos.bundle_total_count", self.env.pos.bundle_total_count)
                        self.env.pos.bundle_products_data = result;
                        self.env.pos.bundle_parent_product = product;
//                        console.log("lkl", result)
                        Gui.showPopup("BundlePopup", {
                            title : _t("Bundle Products"),
                            confirmText: _t("Exit")
                        });
//                        console.log("qwe")
                    });
            }
            else if (product.optional_product_ids[0]){
                var optional_products = []
                var self = this;
                rpc.query({
                        model: 'product.product',
                        method: 'get_product_id',
                        args: [product.optional_product_ids],
                    }).then(function (result) {
                        self.optional_product_product_id = result;
                        for (var i=0;i<result.length; i++){
                            var data= self.env.pos.db.get_product_by_id(result[i]['id']);
                            if (data){
                                data['option_sequence']=result[i].sequence;
                            }
                            optional_products.push(data);
                        }
                        self.env.pos.optional_products_data = optional_products;
                        self.env.pos.optional_parent_product = product;
                        Gui.showPopup("OptionalProductsPopup", {
                            title : _t("Optional Products"),
                            confirmText: _t("Exit")
                        });

                    });
            }
            else{
                let price_extra = 0.0;
                let draftPackLotLines, weight, description, packLotLinesToEdit;

                if (this.env.pos.config.product_configurator && _.some(product.attribute_line_ids, (id) => id in this.env.pos.attributes_by_ptal_id)) {
                    let attributes = _.map(product.attribute_line_ids, (id) => this.env.pos.attributes_by_ptal_id[id])
                                      .filter((attr) => attr !== undefined);
                    let { confirmed, payload } = await this.showPopup('ProductConfiguratorPopup', {
                        product: product,
                        attributes: attributes,
                    });

                    if (confirmed) {
                        description = payload.selected_attributes.join(', ');
                        price_extra += payload.price_extra;
                    } else {
                        return;
                    }
                }

                // Gather lot information if required.
                if (['serial', 'lot'].includes(product.tracking) && (this.env.pos.picking_type.use_create_lots || this.env.pos.picking_type.use_existing_lots)) {
                    const isAllowOnlyOneLot = product.isAllowOnlyOneLot();
                    if (isAllowOnlyOneLot) {
                        packLotLinesToEdit = [];
                    } else {
                        const orderline = this.currentOrder
                            .get_orderlines()
                            .filter(line => !line.get_discount())
                            .find(line => line.product.id === product.id);
                        if (orderline) {
                            packLotLinesToEdit = orderline.getPackLotLinesToEdit();
                        } else {
                            packLotLinesToEdit = [];
                        }
                    }
                    const { confirmed, payload } = await this.showPopup('EditListPopup', {
                        title: this.env._t('Lot/Serial Number(s) Required'),
                        isSingleItem: isAllowOnlyOneLot,
                        array: packLotLinesToEdit,
                    });
                    if (confirmed) {
                        // Segregate the old and new packlot lines
                        const modifiedPackLotLines = Object.fromEntries(
                            payload.newArray.filter(item => item.id).map(item => [item.id, item.text])
                        );
                        const newPackLotLines = payload.newArray
                            .filter(item => !item.id)
                            .map(item => ({ lot_name: item.text }));

                        draftPackLotLines = { modifiedPackLotLines, newPackLotLines };
                    } else {
                        // We don't proceed on adding product.
                        return;
                    }
                }

                // Take the weight if necessary.
                if (product.to_weight && this.env.pos.config.iface_electronic_scale) {
                    // Show the ScaleScreen to weigh the product.
                    if (this.isScaleAvailable) {
                        const { confirmed, payload } = await this.showTempScreen('ScaleScreen', {
                            product,
                        });
                        if (confirmed) {
                            weight = payload.weight;
                        } else {
                            // do not add the product;
                            return;
                        }
                    } else {
                        await this._onScaleNotAvailable();
                    }
                }

                // Add the product after having the extra information.
                this.currentOrder.add_product(product, {
                    draftPackLotLines,
                    description: description,
                    price_extra: price_extra,
                    quantity: weight,
                });

                NumberBuffer.reset();
            }
        }
    }

    Registries.Component.extend(ProductScreen, ProductClick);

    return ProductScreen;


});

