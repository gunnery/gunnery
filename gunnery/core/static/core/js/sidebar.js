var SidebarModule = (function($){
    function updateSideBarHeight() {
        document.querySelector('style').textContent +=
            "@media screen and (min-width:769px) { .side-nav { height: "+$(document).height()+"px; }}";
    }

    $('#department-select').change(function () {
        window.location = window.location.origin + '/department/switch/' + this.value;
    });

    $('#settings-opener').click(function(e){
        e.preventDefault();
        $('#settings-submenu').toggleClass('hide');
        updateSideBarHeight();
    })

    updateSideBarHeight();

    return {};
})(jQuery);




