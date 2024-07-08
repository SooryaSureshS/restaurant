odoo.define('pragmatic_odoo_pos_whatsapp_integration.models', function (require) {
"use strict";

	var models = require('point_of_sale.models');

    models.load_models([{
        model:  'whatsapp.message.template',
        fields: ['id', 'name', 'message'],
        loaded: function(self, msg_templates) {
            self.whatsapp_msg_templates = msg_templates;
        }
    },
    ]);

});