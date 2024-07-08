odoo.define('pos_epson_printer_inherits.printers', function (require) {
"use strict";

const { Gui } = require('point_of_sale.Gui');
var core = require('web.core');
var Printer = require('pos_epson_printer.Printer');
var PrinterMixin = require('point_of_sale.Printer').PrinterMixin;

var _t = core._t;



Printer.include({
    callback_connect: function (resultConnect) {
        var deviceId = 'local_printer';
        var options = {'crypto' : false, 'buffer' : false};
        if ((resultConnect == 'OK') || (resultConnect == 'SSL_CONNECT_OK')) {
            this.ePOSDevice.createDevice(deviceId, this.ePOSDevice.DEVICE_TYPE_PRINTER, options, this.callback_createDevice.bind(this));
        }else {
        swal(
              'Connection to the printer failed',
              'Please check if the printer is still connected, if the configured IP address is correct and if your printer supports the ePOS protocol.',
              'error'
            )
        }
        }
});

});