    
$(document).ready(function(){
	$(function() {
			var a = 0;
			$(window).scroll(function() {
				if ($(this).scrollTop() > 100) {
					if ( $('.counter-box').length > 0 ) {
						var oTop = $('.counter-box').offset().top - window.innerHeight;
						if (a == 0 && $(window).scrollTop() > oTop) {
							$('.counter').each(function () {
						    $(this).prop('Counter',0).animate({
						        Counter: $(this).text()
						    }, {
						        duration: 4000,
						        easing: 'swing',
						        step: function (now) {
						            $(this).text(Math.ceil(now));
						        }
						    	});
							}); 
							a = 1;
						}
					}
				} 
			});
			
		});
	$("#to-top").hide();
    	$(function() {
    		$(window).scroll(function() {
    			if ($(this).scrollTop() > 100) {
    				$('#to-top').fadeIn();
    			} else {
    				$('#to-top').fadeOut();
    			}
    		});
    		$('#to-top a').click(function() {
    			$('body,html').animate({
    				scrollTop : 0
    			}, 800);
    			return false;
    		});
    	});

    var minval = $("input#m1").attr('value'),
        maxval = $('input#m2').attr('value'),
        minrange = $('input#ra1').attr('value'),
        maxrange = $('input#ra2').attr('value'),
        website_currency = $('input#avi_website_currency').attr('value');
    if (!minval) {
        minval = 0;
    }
    if (!maxval) {
        maxval = maxrange;
    }
    if (!minrange) {
        minrange = 0;

    }
    if (!maxrange) {
        maxrange = 2000;
    }

    $("div#priceslider").ionRangeSlider({
        keyboard: true,
        min: parseInt(minrange),
        max: parseInt(maxrange),
        type: 'double',
        from: minval,
        skin: "square",
        to: maxval,
        step: 1,
        prefix: website_currency,
        grid: true,
        onFinish: function(data) {
            $("input[name='min1']").attr('value', parseInt(data.from));
            $("input[name='max1']").attr('value', parseInt(data.to));
            $("div#priceslider").closest("form").submit();
        },
    });
});
$(document).ready(function(){
    $('.progress-value > span').each(function(){
        $(this).prop('Counter',0).animate({
            Counter: $(this).text()
        },{
            duration: 1500,
            easing: 'swing',
            step: function (now){
                $(this).text(Math.ceil(now));
            }
        });
    });
});

$(document).ready(function(){
    $(".close-search").click(function() {
      $(".search-box").removeClass("open");
    });
});

$(document).ready(function(){
    var target = $('#wsale_products_categories_collapse > ul > li > .nav-link.active');
    var prev_li = $(target).parent();
    if ($(target).hasClass("active")){
        $(prev_li).addClass("active");
    } else {}
});

$(document).ready(function(){
    var hierarchy_target = $('.nav-hierarchy > li > .nav-link.active');
    var hierarchy_li = $(hierarchy_target).parent();
    if ($(hierarchy_target).hasClass("active")){
        $(hierarchy_li).addClass("active");
    } else {}
});

$(document).ready(function() {
  if ($('#product_detail_tabs .nav-item').hasClass("nav-item")){
    $('.main-tab').addClass('card-header');
  }
});

$(document).ready(function() {
  $("a.active").find('.mycheckbox').prop('checked', true);
});