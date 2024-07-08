odoo.define('pos_ui_changes.productParentCategory', function(require) {
    'use strict';

    var rpc = require('web.rpc');
    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const PopupControllerMixin = require('point_of_sale.PopupControllerMixin')
    const Chrome = require('point_of_sale.Chrome');
    var models = require('point_of_sale.models');
      const { posbus } = require('point_of_sale.utils');

    /* Return Order button for view the kitchen screen for managers */
    class ParentCategorySearchByProduct extends PosComponent {
        constructor() {
            super(...arguments);
//            useListener('click', this.onClick);
        }
        mounted() {
//            posbus.on('table-set', this, this.render);
        }
        willUnmount() {
//            posbus.on('table-set', this);
        }

        get ParentCategory() {
            console.log("informationsssssss",this.env.pos.db.get_category_childs_ids(0).map(id => this.env.pos.db.get_category_by_id(id)));
//            return this.env.pos.db
//                .get_category_childs_ids(0)
//                .map(id => this.env.pos.db.get_category_by_id(id));
            return 'gggg'
        }
    }
        ParentCategorySearchByProduct.template = 'ParentCategorySearchByProduct';

    Registries.Component.add(ParentCategorySearchByProduct);

    return ParentCategorySearchByProduct;

    });