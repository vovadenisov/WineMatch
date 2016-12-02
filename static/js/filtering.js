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
});
