odoo.define('point_of_sale.productCategoryInherited', function(require) {
    'use strict';

    const { useState } = owl.hooks;
    const PosComponent = require('point_of_sale.PosComponent');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const ProductsWidget = require('point_of_sale.ProductsWidget');


        const ProductsWidgetCategory = (ProductsWidget) =>
        class extends ProductsWidget {
               constructor() {
                    super(...arguments);
               }
               mounted() {
                    this.env.pos.on('change:selectedCategoryId', this.render, this);
                }
                willUnmount() {
                    this.env.pos.off('change:selectedCategoryId', null, this);
                }
                get selectedCategoryId() {
                    var self = this;
                    this.env.pos.db.parent_category = this.env.pos.db.get_category_childs_ids(0).map(id => this.env.pos.db.get_category_by_id(id));
                    var selectedCategoryId = this.env.pos.get('selectedCategoryId')
                      if (selectedCategoryId) {
                        var sub_category = this.env.pos.db.get_category_childs_ids(selectedCategoryId);
                        var parent_category = this.env.pos.db.get_category_parent_id(selectedCategoryId);
                        if (sub_category && !parent_category){
                            var c = 0;
                            _.each(sub_category, function(cate){
                                if (c == 0 && cate) {
                                    self.env.pos.set('selectedCategoryId', cate);
                                }
                                c = c + 1;
                            });
                        }
                    }
                    return this.env.pos.get('selectedCategoryId');
                }
               get subcategories() {
                    return this.env.pos.db
                        .get_category_childs_ids(this.selectedCategoryId)
                        .map(id => this.env.pos.db.get_category_by_id(id));
                }
                 get parentCategory() {
                    return this.env.pos.db
                        .get_category_childs_ids(this.selectedCategoryId)
                        .map(id => this.env.pos.db.get_category_by_id(id));
                }
              _switchCategory(event) {
                    $('#product_filters_informations').val("Filter");
                    $('.product-list-container .product-list #product_info_list').each(function(){
                        $(this).show();
                    });
                    this.env.pos.set('selectedCategoryId', event.detail);
                }
                get breadcrumbs() {
                    if (this.selectedCategoryId === this.env.pos.db.root_category_id) return [];
                    var c = [
                        ...this.env.pos.db
                            .get_category_ancestors_ids(this.selectedCategoryId)
                            .slice(1),
                        this.selectedCategoryId,
                    ].map(id => this.env.pos.db.get_category_by_id(id));

                    if (this.env.pos.db.get_category_parent_id(this.selectedCategoryId)) {

                         var list = [
                                ...this.env.pos.db
                                    .get_category_childs_ids(this.env.pos.db.get_category_parent_id(this.selectedCategoryId))
                            ].map(id => this.env.pos.db.get_category_by_id(id));
                        var q = this.env.pos.db.get_category_by_id(this.env.pos.db.get_category_parent_id(this.selectedCategoryId))

                        var list1 = []
                        list1.push(q);
                        for (var i=0;i<list.length;i++){
                                 list1.push(list[i]);
                        }
                         return list1
                    }else{
                         return [
                                ...this.env.pos.db
                                    .get_category_ancestors_ids(this.selectedCategoryId)
                                    .slice(1),
                                this.selectedCategoryId,
                            ].map(id => this.env.pos.db.get_category_by_id(id));
                    }

                }


        };

    Registries.Component.extend(ProductsWidget, ProductsWidgetCategory);

    return ProductsWidget;

    });