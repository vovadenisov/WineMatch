/**
 * Created by v.denisov on 14.11.16.
 */


$(document).ready(function(){
    var is_adult = localStorage.getItem("is_adult");
    if(!is_adult){
        is_adult_text = $("<div>").text("Я подтверждаю, что мне больше 18 лет");
        is_adult_text.dialog({
            modal:true,
            close: function (e) {
                localStorage.setItem("is_adult", "confirm")
            }
        })
    }
});