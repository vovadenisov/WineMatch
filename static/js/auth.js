/**
 * Created by v.denisov on 12.09.16.
 */


$(document).ready(function(){
    $('.js-login').click(function(e){
        e.preventDefault();
        $(".js-login-block").dialog({
            width: 500,
            height: 400
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
