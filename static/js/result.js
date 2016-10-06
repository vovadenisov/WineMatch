/**
 * Created by v.denisov on 29.09.16.
 */
$(document).ready(function(){
    $(".result-wrapper").slick({
        dots: false,
        infinite: true,
        speed: 500,
        fade: true,
        cssEase: 'linear'
    });
    $(".js-slick-navigation-right").click(function(){
        $(".slick-next").click();
    });

    $(".js-slick-navigation-left").click(function(){
        $(".slick-prev").click();
    })

});
