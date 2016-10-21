/**
 * Created by v.denisov on 12.09.16.
 */


$(document).ready(function(){
    $('.js-login').click(function(e){
        e.preventDefault();
        var max_width = $(window).width() * 0.8;
        var max_height = $(window).height() * 0.8;
        $(".js-login-block").dialog({
            modal: true,
            width: Math.min(max_width, 500),
            height: Math.min(max_height, 400),
            open: function( event, ui ) {
                $(".ui-widget-overlay").click(function () {
                    $(".js-login-block").dialog("close")
                });
                $(".content-wrapper, .result-wrapper, .survey-wrapper").addClass("blur-filter");
            },
            close: function( event, ui ) {
                $(".blur-filter").removeClass("blur-filter");
            }
        });
    });

    VK.init({
        apiId: 5630203
    });
    $(".js-vk-login").on("click", function(){
        VK.Auth.login(
            function(data){
                $.ajax({
                    url: USER_VK_AUTH_URL,
                    data: {"mid": data.session.mid},
                    success: function(){
                        location.reload();
                    }
                });
            }
        )
    });
});
