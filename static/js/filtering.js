//Dropdown
//Toggle animation
$(document).ready(function () {
    $('.toggleDropdown').click(function(event) {
        $(this).closest(".js-choice-container").find('.filters__dropdown__body').slideToggle(200);
    });
    //Choice
    $('.filters__dropdown__choice').click(function(event) {
        var content = $(this).text();
        $(this).closest(".js-choice-container").find('.countryChoice').val(content);
    });

    console.log("input")

    $("input").on("change", function(){
        console.log("change");
        var form = $(this).closest("form")
        var data = form.serialize()
        var url = form.data("url")
        $.ajax({
            url: url,
            data: data,
            method: "get",
            success: function(data){
                var cont = $(".js-container");
                cont.html(data)
            },
            error: function(data){
                alert("error")
            }
        })
    })
});
