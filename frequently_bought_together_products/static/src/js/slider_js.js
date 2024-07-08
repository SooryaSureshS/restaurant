$(document).ready(function() {

var sync1 = $("#sync1");
var sync2 = $("#frequently-bought-products");

      sync2.owlCarousel({
        items : 3,
        itemsDesktop      : [1199,10],
        itemsDesktopSmall     : [979,10],
        itemsTablet       : [768,8],
        itemsMobile       : [479,8],
        pagination:true,
        responsiveRefreshRate : 100,
       
      });

      function syncPosition(el){
        var current = this.currentItem;
        $("#frequently-bought-products")
          .find(".owl-item")
          .removeClass("synced")
          .eq(current)
          .addClass("synced")
        if($("#frequently-bought-products").data("owlCarousel") !== undefined){
          center(current)
        }

      }

      function center(number){
        var sync2visible = sync2.data("owlCarousel").owl.visibleItems;

        var num = number;
        var found = false;
        for(var i in sync2visible){
          if(num === sync2visible[i]){
            var found = true;
          }
        }

        if(found===false){
          if(num>sync2visible[sync2visible.length-1]){
            sync2.trigger("owl.goTo", num - sync2visible.length+2)
          }else{
            if(num - 1 === -1){
              num = 0;
            }
            sync2.trigger("owl.goTo", num);
          }
        } else if(num === sync2visible[sync2visible.length-1]){
          sync2.trigger("owl.goTo", sync2visible[1])
        } else if(num === sync2visible[0]){
          sync2.trigger("owl.goTo", num-1)
        }
      }



});