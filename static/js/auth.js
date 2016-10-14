/**
 * Created by v.denisov on 12.09.16.
 */


$(document).ready(function(){
    $('.js-login').click(function(e){
        console.log("2222 login");
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
        console.log("3333 js-vk")
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
