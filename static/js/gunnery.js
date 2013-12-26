(function( $ ){
	$.fn.subformMultiple = function () {
		function onRowChange(el) {
			el.find('.button-up').css('visibility', 'visible').first().css('visibility', 'hidden');
			el.find('.button-down').css('visibility', 'visible').last().css('visibility', 'hidden');
		}
		
		this.each(function(i, el) {
			el = $(el);
			var dataModel = el.data('model'),
				totalFormsInput = el.find('#id_'+dataModel+'-TOTAL_FORMS'),
				totalForms = parseInt(totalFormsInput.val());
			el.find('.button-up').click(function(){
				var thisSubform = $(this).parents('.form-group');
				thisSubform.prev().before(thisSubform);
				onRowChange(el);
			});
			el.find('.button-down').click(function(){
				var thisSubform = $(this).parents('.form-group');
				thisSubform.next().after(thisSubform);
				onRowChange(el);
			});
			el.find('.button-add').click(function(){
				var sample = el.find('.form-group').first(),
					newRow = sample.clone(true, true).removeClass('hide');
				newRow.find('input,select,textarea').each(function(i,input){
					input.name = input.name.replace('-0-', '-'+totalForms+'-');
					input.value = '';
				});
    			totalFormsInput.val(++totalForms);
				el.find('.form-group.actions').before(newRow);
				onRowChange(el);
				newRow.find(".chosen-select")
					.chosen({width: '100%'});
			});
			el.find('.button-remove').click(function(){
				var subform = $(this).parents('.form-group');
				if (!subform.find('input.input-id').val()) {
					subform.remove();
				} else if (confirm('Are you sure?')) {
					subform.hide().find('input.input-delete').val('on');
				}
				onRowChange(el);
			});

			onRowChange(el);
		});
	};
	$('.subform-multiple').subformMultiple();
})( jQuery );

$('.execution-list-inline .well').click(function(event){
	window.location = $(this).find('a')[0].href;
});

$(document.body).on('hidden.bs.modal', function () {
	$('#large-modal').removeData('bs.modal')
});

$(document.body).on('shown.bs.modal', function () {
	$('#large-modal').find('.form-group input,.form-group select,.form-group textarea').first().focus();
});

(function( $ ){
	$('[data-toggle="element"').click(function(event){
		$($(this).data('target')).toggleClass('hide');
	});
	$(".chosen-select").chosen({width: '100%'});


	function modalAjaxHandler(form) {
		return function(data, status, response) {
			var contentType = response.getResponseHeader('Content-Type');
			if (contentType.match(/text/)) {
				form.parents('.modal-body').html(data);
			} else if (contentType.match(/json/)) {
				form.parents('.modal').find('.cancel').click();
				if (data.action == 'reload') {
					window.location = window.location;
					window.location.reload();
				}
			}
		}
	}
	function modalSaveHandler(event) {
		event.preventDefault();
		var form = $(this).parents('.modal-content').find('form[role="form"]');
		$.post(form.attr('action'), form.serialize(), modalAjaxHandler(form));
	}
	function modalDeleteHandler(event) {
		if (confirm('Are you sure?')) {
			var form = $(this).parents('.modal-content').find('form[role="delete"]');
			$.post(form.attr('action'), form.serialize(), modalAjaxHandler(form));
		}
	}
	$('body').on('click', '.modal .save', modalSaveHandler);
	$('body').on('submit', '.modal form', modalSaveHandler);
	$('body').on('click', '.modal .delete', modalDeleteHandler);
})( jQuery );