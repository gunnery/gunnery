$('.execution-list-inline .well').click(function (event) {
    window.location = $(this).find('a')[0].href;
});

(function ($) {
    $('.sessionMessageWrap div').addClass('show').each(function(i, e){
        e = $(e);
        if (!e.hasClass('error')) {
            setTimeout(function(){$(e).removeClass('show')}, e.text().length*256);
        }
    }).click(function(){
        $(this).removeClass('show');
    });
})(jQuery);
