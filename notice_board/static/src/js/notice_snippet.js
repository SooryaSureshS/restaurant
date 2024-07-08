/* Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('notice_board.notice_board_snippet', function (require) {
    "use strict";

    var ajax = require('web.ajax');

    $(document).ready(get_notices);
    $(window).on('resize',get_notices);

    function get_notices() {
        var notice_count;
        if ($(window).width() >= 992){
            notice_count = 3;
        }
        else if($(window).width() >= 768 && $(window).width() < 992){
            notice_count = 2;
        }
        else{
            notice_count = 1;
        }

        ajax.jsonRpc("/get/notices", 'call', {'notice_count':notice_count,
            }).then(function (result) {
                $('#notice_carousel').html(result['template']);
                $('.notice-box').on("click", function (e) {
                    e.preventDefault();
                    var data = $(this).closest('.notice-box').html();
                    $('#current_notice').html(data);
                    $('#noticeModal').appendTo('body');
                    $('#noticeModal').modal('show');
                });
            });
    }
});
