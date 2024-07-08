odoo.define('pos_ui_changes.modelsUi', function (require) {
"use strict";

var models = require('point_of_sale.models');
const { Gui } = require('point_of_sale.Gui');
const { posbus } = require('point_of_sale.utils');

models.load_fields("product.product", ['v','gf','df','veg','is_optional_product']);
models.load_fields("pos.category", ['color', 'hide_in_categories']);
});