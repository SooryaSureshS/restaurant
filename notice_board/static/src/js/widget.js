/* Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('notice_board.widget', function (require) {
    "use strict";

    var core = require('web.core');
    var SystrayMenu = require('web.SystrayMenu');
    var Widget = require('web.Widget');
    var ajax = require('web.ajax');
    var web_client = require('web.web_client');
    var QWeb = core.qweb;
    var _t = core._t;

    var NoticeRecord = Widget.extend({
        template:'notice_board.Notices',
        start: function () {
            this.notice_dropdown_records = this.$('.notice_dropdown');
            this._updatewidget();
            return this._super();
        },
        _getNoticeData: function(){
            var self = this;
            return ajax.jsonRpc("/get/notice/records", 'call', {}).then(
                function(data) {
                    self.records = data;
                }
            );
        },
        _updatewidget: function(){
            var self = this;
            self._getNoticeData().then(function(){
                self.notice_dropdown_records.html(QWeb.render('notice_board.NoticeRecords', {
                    records : self.records
                }));
            });
        },
    });
    SystrayMenu.Items.push(NoticeRecord);
    });
