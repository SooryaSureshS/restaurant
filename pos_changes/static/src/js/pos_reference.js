odoo.define('pos_changes.models', function (require) {
"use strict";


    const { Context } = owl;
    const pos_model = require('point_of_sale.models');
    var core = require('web.core');
    var _t = core._t;
    var _super_order = pos_model.Order.prototype;
    pos_model.load_fields('res.company', 'branch_code');

    pos_model.Order = pos_model.Order.extend({
        initialize: function(attributes,options) {
            _super_order.initialize.call(this,attributes,options);
            this.inv_name = this.inv_name || "";
            this.set_inv_name()
            if (options.json) {
                console.log()
                   // Duplicate Product Issue so this code is commit
//                this.init_from_JSON(options.json);
            } else {
                this.sequence_number = this.pos.pos_session.sequence_number++;
//                this.uid  = this.generate_unique_id();
//                this.name = _.str.sprintf(_t("INV-%s-%s"), this.pos.company.branch_code, this.uid);
                this.validation_date = undefined;
                this.fiscal_position = _.find(this.pos.fiscal_positions, function(fp) {
                    return fp.id === self.pos.config.default_fiscal_position_id[0];
                });
            }
        },

        export_as_JSON: function() {
			var self = this;
			var loaded = _super_order.export_as_JSON.call(this);
			loaded.inv_name = self.inv_name;
			return loaded;
		},

        init_from_JSON: function(json){
            _super_order.init_from_JSON.apply(this,arguments);
//            this.name = _.str.sprintf(_t("INV-%s-%s"), this.pos.company.branch_code, this.uid);
            this.inv_name = json.inv_name;
        },

        set_inv_name: function(){
            var self = this;
			self.inv_name = _.str.sprintf(_t("INV-%s-%s"), this.pos.company.branch_code, this.generate_unique_inv_id());
		},

		get_inv_name: function(){
			return this.inv_name;
		},

        generate_unique_inv_id: function() {
            function zero_pad(num,size){
                var s = ""+num;
                while (s.length < size) {
                    s = "0" + s;
                }
                return s;
            }
            return zero_pad(this.sequence_number, 4);
        }
    });

    return pos_model;
});


odoo.define('pos_changes.OrderReceipt', function(require) {
	"use strict";

	const OrderReceipt = require('point_of_sale.OrderReceipt');
	const Registries = require('point_of_sale.Registries');
	var time_module = require('web.time');

	const BiOrderReceipt = OrderReceipt =>
		class extends OrderReceipt {
			constructor() {
				super(...arguments);
			}

			get receipt() {
			    let res = super.receipt;
				let inv_name = this.env.pos.get_order().get_inv_name();
                res['current_date'] = time_module.datetime_to_str(new Date());
                res['inv_name'] = inv_name;
				return res;
			}

	};

	Registries.Component.extend(OrderReceipt, BiOrderReceipt);

	return OrderReceipt;
});