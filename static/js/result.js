/**
 * Created by v.denisov on 29.09.16.
 */


$(document).ready(function(){
    //ajax setup
    function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
        }
    });

    //result page
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
    });

    $(".js-get-it") .click(function(ev) {
        ev.preventDefault();
         $.ajax({
             type: "POST",
             url: '/feedback/ajax/selectwine/',
             data: 'wine_id=' + $(ev.target).data('id'),
             success: function() {
                 $('.js-selected').children().show();
                 $('.js-hide-on-selection').hide();
                 $(".result-wrapper").unslick();
             },
             error: function() {
                 console.log('error');
             }
         });    
       
    });
    
    $(".js-see-more") .click(function(event) {
        event.preventDefault();
        $(".slick-next").click();
    });
    
    //feedback page
    var rating = 0;
    var baseUrl = window.location.protocol + "//" + window.location.host;
    $('.js-answer').click(function(ev) {
        ev.preventDefault();
        $.ajax({
             type: "POST",
             url: '/feedback/ajax/answer/',
             data: 'rating=' + rating + '&comment=' + ($('.js-comment').val() || ''),
             success: function() {
                 window.location.href = baseUrl + '/thnx/';
                 //console.log('success');
             },
             error: function() {
                 console.log('error');
             }
        });     
    });
    
    $('.js-decline').click(function(ev) {
        ev.preventDefault();
        $.ajax({
             type: "POST",
             url: '/feedback/ajax/decline/',
             success: function() {
                 window.location.href = baseUrl + '/thnx/?declined=true';
             },
             error: function() {
                 console.log('error');
             }
         }); 
    });  
    
    $('.js-rating').click(function(ev) {
        rating = $(ev.target).data('rating');
        for (var i = 1; i <= rating; ++i) {
            $('#js-rating-' + i).removeClass('fa-star-o').addClass('fa-star');    
        }
        
        for (var i = rating + 1; i <= 5; ++i) {
            $('#js-rating-' + i).removeClass('fa-star').addClass('fa-star-o');
        }    
    });  
});
