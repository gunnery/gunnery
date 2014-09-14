var TaskFormModule = (function($){
    function taskAjaxHandler(form) {
        return function (data, status, response) {
            var contentType = response.getResponseHeader('Content-Type');
            if (contentType.match(/text/)) {
                form.parents('.modal-body').html(data);
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

    function taskDeleteHandler(event) {
        if (confirm('Are you sure?')) {
            var form = $('form[role="delete"]');
            $.post(form.attr('action'), form.serialize(), taskAjaxHandler(form));
        }
    }

    $.fn.subformMultiple = function () {
        function onRowChange(el) {
            el.find('.button-up').css('visibility', 'visible').first().css('visibility', 'hidden');
            el.find('.button-down').css('visibility', 'visible').last().css('visibility', 'hidden');
            if (el.find('.form-group:visible').length<=2) {
                el.find('.button-remove').hide();
            } else {
                el.find('.button-remove').show();
            }
        }

        function setOrderFields(subform) {
            subform.find('.form-group').each(function (i, el) {
                el = $(el);
                if (el.find('input[type="text"]').val() != '') {
                    $(el).find('.input-order').val(i);
                }
            });
        }

        this.each(function (i, el) {
            el = $(el);
            var dataModel = el.data('model'),
                totalFormsInput = el.find('#id_' + dataModel + '-TOTAL_FORMS'),
                totalForms = parseInt(totalFormsInput.val());
            el.find('.button-up').click(function () {
                var thisSubform = $(this).parents('.form-group');
                thisSubform.prev().before(thisSubform);
                onRowChange(el);
            });
            el.find('.button-down').click(function () {
                var thisSubform = $(this).parents('.form-group');
                thisSubform.next().after(thisSubform);
                onRowChange(el);
            });
            el.find('.button-add').click(function () {
                var sample = el.find('.form-group').first(),
                    newRow = sample.clone(true, true).show();
                newRow.find('input,select,textarea').each(function (i, input) {
                    input.name = input.name.replace('-0-', '-' + totalForms + '-');
                    input.value = '';
                });
                totalFormsInput.val(++totalForms);
                el.find('.form-group.actions').before(newRow);
                onRowChange(el);
                newRow.find(".chosen-select").chosen({width: '100%'});
            });
            el.find('.button-remove').click(function () {
                var subform = $(this).parents('.form-group');
                if (!subform.find('input.input-id').val()) {
                    subform.remove();
                } else if (confirm('Are you sure?')) {
                    subform.detach().hide().find('input.input-delete').val('on');
                    $('.removed').append(subform);
                }
                onRowChange(el);
            });
            el.parents('form').submit(function (event) {
                setOrderFields(el);
            });
            onRowChange(el);
        });
    };
    $('.subform-multiple').subformMultiple();

    $('form .delete').click(taskDeleteHandler);
    $('[data-toggle="element"]').click(function (event) {
        $($(this).data('target')).toggleClass('hide');
    });

    return {};
})(jQuery);
