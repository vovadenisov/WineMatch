/**
 * Created by v.denisov on 27.09.16.
 */

$(document).ready(function(){
    $(".show-menu").click(function (e) {
        e.preventDefault();
        $(this).parent("nav").addClass("menu-active");
        $(this).hide();
        $(".close-menu").show()
    });
    $(".close-menu").click(function (e) {
        e.preventDefault();
        $(this).parent("nav").removeClass("menu-active");
        $(this).hide();
        $(".show-menu").show()
    });
});

function getParameters() {
    var searchString = window.location.search.substring(1),
    params = searchString.split("&"),
    hash = {};

    if (searchString == "") return {};
    for (var i = 0; i < params.length; i++) {
        var val = params[i].split("=");
        hash[unescape(val[0])] = decodeURIComponent(val[1]);
    }

    return hash;
}

$(document).ready(function() {
    var param = getParameters();
    if (typeof param.query != 'undefined') {
        $('.js-search-value').val(param.query);
    }
    $('.js-search').click(function() {
        var query = $('.js-search-value').val();
        if (query && query.length > 2) {
            window.location.href = '/search/?query=' + query;
        }
    });
});