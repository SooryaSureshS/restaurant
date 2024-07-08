$( document ).ready(function() {
var list_dict = [];
        $('body').find('label').each(function(){
            $(this).addClass('trn');
            list_dict.push($(this).text())
        });
        $('body').find('span').each(function(){
            $(this).addClass('trn');
            list_dict.push($(this).text())
        });
         $('body').find('button').each(function(){
            $(this).addClass('trn');
            list_dict.push($(this).text())
        });
        $('body').find('a').each(function(){
            $(this).addClass('trn');
            list_dict.push($(this).text())
        });
         $('body').find('h5').each(function(){
            $(this).addClass('trn');
            list_dict.push($(this).text())
        });
        $('body').find('h4').each(function(){
            $(this).addClass('trn');
            list_dict.push($(this).text())
        });
        $('body').find('h3').each(function(){
            $(this).addClass('trn');
            list_dict.push($(this).text())
        });
        $('body').find('h2').each(function(){
            $(this).addClass('trn');
            list_dict.push($(this).text())
        });
        $('body').find('h1').each(function(){
            $(this).addClass('trn');
            list_dict.push($(this).text())
        });


    console.log( "ready! function trigger",list_dict );
});