odoo.define('language_transulator.transulate', function (require) {
	"use strict";

$( document ).ready(function() {
    $( "a" ).mousedown(function(ev) {
        console.log("eee",$(ev.currentTarget).attr('href'))
        if ($(ev.currentTarget).attr('href')!= '#' ) {
            $('#wrapwrap').hide();
         $.blockUI({
            message: 'Page loading ...',
            timeout: 2000
        });
           setTimeout(function () {
                            $('#wrapwrap').show();
           }, 1000);
        window.location.href=$(ev.currentTarget).attr('href')
        }

    });
//        $('body').block({
//                message: '<lottie-player src="https://assets9.lottiefiles.com/packages/lf20_p8bfn5to.json"  background="transparent"  speed="1"  style="height: 300px;"  loop autoplay></lottie-player>',
//                overlayCSS: {backgroundColor: "#000", opacity: 1, zIndex: 1050, color: "#000000"},
//        });
        $('#wrapwrap').show();
    $.ajax({
                type: 'POST',
                url: window.location.origin + '/language/transition',
                dataType: 'json',
                beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                data: JSON.stringify({jsonrpc: '2.0'}),

                success: function(data) {
                    console.log("ta",data)
                    if (data.result) {
                        var dict2 = data.result['language'];
                        console.log("ssssss",$('body').find('label'))
                        $('body').find('label').each(function(){
                            $(this).addClass('trn');
                        });
                        $('body').find('span').each(function(){
                            $(this).addClass('trn');
                        });
                         $('body').find('button').each(function(){
                            $(this).addClass('trn');
                        });
//                        $('body').find('a').each(function(){
//                            $(this).addClass('trn');
//                        });
                         $('body').find('h5').each(function(){
                            $(this).addClass('trn');
                        });
                        $('body').find('h4').each(function(){
                            $(this).addClass('trn');
                        });
                        $('body').find('h3').each(function(){
                            $(this).addClass('trn');
                        });
                        $('body').find('li').each(function(){
                            $(this).addClass('trn');
                        });
                        $('body').find('h2').each(function(){
                            $(this).addClass('trn');
                        });
                        $('body').find('h1').each(function(){
                            $(this).addClass('trn');
                        });
//                          $('body').find('a').each(function(){
//                            $(this).addClass('trn');
//                        });

                        var _t = $('body').translate({lang: data.result['code'], t: dict2});
                        var str = _t.g("translate");
//                        $(document).ajaxStop($.unblockUI);
                        setTimeout(function () {
//                                $('body').unblock();
                            $.unblockUI();
                            }, 1000);
                    }
                }
    });
//    var dict = {
//        "Classic White": {
//          fr: "Bonjour le monde",
//          cn: "你好世界"
//        },
//      };
//      var translator = $('body').translate({lang: "en", t: dict});
//    var _t = $('body').translate({lang: "cn", t: dict});
//    var str = _t.g("translate");
    console.log( "ready! function trigger" );
});

});