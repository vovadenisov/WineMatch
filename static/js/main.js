
//# sourceMappingURL=data:application/json;charset=utf8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIm1haW4uanMiXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IiIsImZpbGUiOiJtYWluLmpzIiwic291cmNlc0NvbnRlbnQiOlsiLy89IGNvbXBvbmVudHMvaGVhZGVyL2hlYWRlci5qc1xuLy89IGNvbXBvbmVudHMvc3RhcnRfc2xpZGVyL3N0YXJ0X3NsaWRlci5qc1xuIl19

$(document).ready(function() {
    //is adult
    (function () {
	var showAdult = function() {
        $('.js-is-not-adult').fadeOut();
        $('.js-is-adult').fadeIn();	
        var startSwiper = new Swiper('.start_slider__swiper', {
            speed: 400,
            loop: true,
            autoplay: 5000
        });
    };

    var is_adult = localStorage.getItem("is_adult");
    
    if(!is_adult) {
        $('#js-confirm-adult').click(function() {
            localStorage.setItem("is_adult", "confirm");
            showAdult();
        })
    } else {
        showAdult();
    }

    $('.js-select-wine').click(function() {
        window.location.href = '/find/';
    });

    })();

    //questions
    (function() {
        var answerId;
        $('.js-select-answer').click(
            function(ev) {
                ev.preventDefault();
                $('.js-answer-for-deactivate').removeClass('active').addClass('deactive');
                $(ev.target).removeClass('deactive').addClass('active');
                answerId = $(ev.target).data('id');
                $('.js-go-to-next').addClass('active');
            }
        )
        $('.js-go-to-next').click(function(ev) {
            ev.preventDefault();
            if (!(answerId)) { return; }
            window.location.href = '/find/?answer=' + answerId + '&survey=' + $(ev.target).data('id');
        });
    })();

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
    //shop
    (function() {
        $('.js-change-fav').click(function(ev) {
            ev.preventDefault();
            $.ajax({
                type: "POST",
                url: '/favorite/ajax/toggle/',
                data: 'wine_id=' + $(ev.target).data('id'),
                success: function() {
                    $(ev.target).toggleClass('active');
                },
                error: function() {
                   console.log('error');
                }
            });
        });

        $('.js-show-description').click(function(ev) {
            ev.preventDefault();
            $('#js-where-to-buy__' + $(ev.target).data('id')).fadeOut();
            $('#js-main-description__' + $(ev.target).data('id')).fadeIn();
        });

        $('.js-show-where-to-buy').click(function(ev) {
            ev.preventDefault();
            $('#js-main-description__' + $(ev.target).data('id')).fadeOut();
            $('#js-where-to-buy__' + $(ev.target).data('id')).fadeIn();
        });

        $('.js-go-to-shop').click(function(ev) {
            ev.preventDefault();
             window.location.href = $(ev.target).data('href');
        });

    })();
});
