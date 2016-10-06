/**
 * Created by v.denisov on 27.09.16.
 */

$(document).ready(function(){
    $(".show-menu").click(function (e) {
        $(this).parent("nav").addClass("menu-active");
        $(this).hide();
        $(".close-menu").show()
    })
    $(".close-menu").click(function (e) {
        $(this).parent("nav").removeClass("menu-active");
        $(this).hide();
        $(".show-menu").show()
    })
});
