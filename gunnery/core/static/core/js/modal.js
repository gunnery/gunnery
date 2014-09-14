var ModalModule = (function($){
    var body = $(document.body);
    function modalAjaxHandler(form) {
        return function (data, status, response) {
            var contentType = response.getResponseHeader('Content-Type');
            if (contentType.match(/text/)) {
                form.parents('.modal-body').html(data);
                $('.modal .save').prop('disabled', false);
            } else if (contentType.match(/json/)) {
                form.parents('.modal').find('.cancel').click();
                if (data.action == 'reload') {
                    window.location = window.location;
                    window.location.reload();
                } else if (data.action == 'redirect') {
                    window.location = data.target;
                }
            }
        }
    }

    function modalSaveHandler(event) {
        event.preventDefault();
        $(this).prop('disabled', true);
        var form = $(this).parents('.modal-content').find('form[role="form"]');
        $.post(form.attr('action'), form.serialize(), modalAjaxHandler(form));
    }

    function modalDeleteHandler(event) {
        if (confirm('Are you sure?')) {
            $(this).prop('disabled', true);
            var form = $(this).parents('.modal-content').find('form[role="delete"]');
            $.post(form.attr('action'), form.serialize(), modalAjaxHandler(form));
        }
    }

    body.on('click', '.modal .save', modalSaveHandler);
    body.on('submit', '.modal form', modalSaveHandler);
    body.on('click', '.modal .delete', modalDeleteHandler);
    $(".chosen-select").chosen({width: '100%'});
    $(document.body).on('hidden.bs.modal', function () {
        $('#large-modal').removeData('bs.modal').find('.modal-body').html('');
    });

    $(document.body).on('shown.bs.modal', function () {
        setTimeout(function() {
            $('#large-modal').find('.form-group input,.form-group select,.form-group textarea').first().focus();
        }, 200);
    });

    return {};
})(jQuery);