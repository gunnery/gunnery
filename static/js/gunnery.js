(function( $ ){
	$.fn.tagSelect = function () {
		this.each(function(i, el) {
			var el = $(el),
				tags = el.data('tags').split(' '),
				name = el.data('name'),
				tagsSelected = el.data('tags-selected').split(' '),
				tagsMultiple = el.data('tags-multiple') == 1;
			
			// make html
			el.html('');
			el.append('<input type="hidden" name="'+name+'" value="'+tagsSelected.join(' ')+'"/>');
			$.each(tags, function(i, tag){
				var selected = tagsSelected.indexOf(tag) !== -1 ? 'selected' : '';
				el.append('<span class="label label-default '+selected+'">'+tag+'</span> ');
			});

			// bind click event
			el.find('span').click(function(event){
		  		$(this).toggleClass('selected');
				var selected = [];
				el.find('span.selected').each(function(i, tag) {
					selected.push($(tag).text());
				});
				el.find('input').val(selected.join(' '));
			});
			
			return el;
		});
	};

	$('.tag-select').tagSelect();
})( jQuery );

(function( $ ){
	$.fn.subformMultiple = function () {
		function onRowChange(el) {
			el.find('.button-up').css('visibility', 'visible').first().css('visibility', 'hidden');
			var downs = el.find('.button-down').css('visibility', 'visible');
			downs.eq(downs.length-2).css('visibility', 'hidden');
		}
		this.each(function(i, el) {
			el = $(el);
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
				var template = el.find('.form-template'),
					newRow = template.clone(true, true).removeClass('hide').removeClass('form-template');
				template.before(newRow);
				onRowChange(el);
				el.find('.tag-select').tagSelect();
			});
			el.find('.button-remove').click(function(){
				if (confirm('Are you sure?')) {
					$(this).parents('.form-group').remove();
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

(function( $ ){
	$('[data-toggle="element"').click(function(event){
		$($(this).data('target')).toggleClass('hide');
	})
	$(".chosen-select").chosen({});
})( jQuery );