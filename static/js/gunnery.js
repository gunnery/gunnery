(function( $ ){
	$.fn.tagSelect = function () {
		var that = this;
		this.each(function() {

		var tags = that.data('tags').split(' '),
			name = that.data('name'),
			tagsSelected = that.data('tags-selected').split(' '),
			tagsMultiple = that.data('tags-multiple') == 1;
			

		// make html
		that.html('');
		that.append('<input type="hidden" name="'+name+'" value="'+tagsSelected.join(' ')+'"/>');
		$.each(tags, function(i, tag){
			var selected = tagsSelected.indexOf(tag) !== -1 ? 'selected' : '';
			that.append('<span class="label label-default '+selected+'">'+tag+'</span> ');
		});

		// bind click event
		that.find('span').click(function(event){
	  		$(that).toggleClass('selected');
			var selected = [];
			that.find('span.selected').each(function(i, tag) {
				selected.push($(tag).text());
			});
			that.find('input').val(selected.join(' '));
		});
		
		return that;
	});
};

	$('.tag-select').tagSelect();
})( jQuery );

(function( $ ){
	$.fn.tagSelectt = function () {
	};
})( jQuery );

$('.execution-list-inline .well').click(function(event){
  window.location = $(this).find('a')[0].href;
});

$(document.body).on('hidden.bs.modal', function () {
  $('#large-modal').removeData('bs.modal')
});