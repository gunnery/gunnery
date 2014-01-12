(function( $ ){
	function taskAjaxHandler(form) {
		return function(data, status, response) {
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
	$('form .delete').click(taskDeleteHandler);
})( jQuery );
