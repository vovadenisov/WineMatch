/**
 * Created by v.denisov on 27.09.16.
 */

$(document).ready(function(){
    $(".show-menu").click(function (e) {
        e.preventDefault();
        console.log(111);
        $(this).parent("nav").addClass("menu-active");
        $("#logo").hide();
        $(this).hide();
        $(".close-menu").show()
    });
    $(".close-menu").click(function (e) {
        e.preventDefault();
        console.log(111);
        $(this).parent("nav").removeClass("menu-active");
        $(this).hide();
        $("#logo").show();
        $(".show-menu").show()
    });
});
