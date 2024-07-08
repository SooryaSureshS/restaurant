odoo.define('pos_size_category.product_category', function(require) {
    'use strict';


	const CashierName = require('point_of_sale.CashierName');
    const Registries = require('point_of_sale.Registries');
    const useSelectEmployee = require('pos_hr.useSelectEmployee');
    const { useBarcodeReader } = require('point_of_sale.custom_hooks');
    const ProductsWidget = require('point_of_sale.ProductsWidget');
    const { useListener } = require('web.custom_hooks');

	const ProductSizeCategory = (ProductsWidget) =>
        class extends ProductsWidget {
            constructor() {
                super(...arguments);
//                const { selectEmployee, askPin } = useSelectEmployee();
//                this.askPin = askPin;
                this.data = "selectEmployee";
                useListener('switch-size-category', this._switchSizeCategory);
//                useBarcodeReader({ cashier: this._onCashierScan });
            }
            mounted() {
//                this.env.pos.on('change:cashier', this.render, this);
            }
            willUnmount() {
//                this.env.pos.off('change:cashier', null, this);
            }
            _switchSizeCategory(event) {
                console.log("size")
//                this.env.pos.set('selectedCategoryId', event.detail);
            }

        get product_size_categorys() {
            console.log("data found",this.env.pos.product_size_category)
            return this.env.pos.product_size_category
        }
        };

    Registries.Component.extend(ProductsWidget, ProductSizeCategory);

    return ProductSizeCategory;

	
//   const { Gui } = require('point_of_sale.Gui');
//   const PosComponent = require('point_of_sale.PosComponent');
//   const { posbus } = require('point_of_sale.utils');
//   const ProductScreen = require('point_of_sale.ProductScreen');
//   const { useListener } = require('web.custom_hooks');
//   const Registries = require('point_of_sale.Registries');
//   const PaymentScreen = require('point_of_sale.PaymentScreen');
//
//   class ProductSizeCategory extends PosComponent {
//       constructor() {
//           super(...arguments);
////           useListener('click', this.onClick);
////            this.productSizeCategory = this.env.pos.product_size_category;
////            console.log("this",this)
////                this.state = useState({ searchWord: '' });
//       }
//
//
//        get hasNoCategories() {
//            return this.env.pos.db.get_category_childs_ids(0).length === 0;
//        }
//   }
//   ProductSizeCategory.template = 'ProductSizeCategory';
//
//   Registries.Component.add(ProductSizeCategory);
//   return ProductSizeCategory;
});
	
