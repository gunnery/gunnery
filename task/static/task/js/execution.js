(function( $ ){
	var handlers = {
		command_output: function(data) {
			var el = $('.server[data-command-server-id="'+data.command_server_id+'"] pre');
			el.append(data.output);
		},
		command_completed: function(data) {
			var text, tclass, el = $('.server[data-command-server-id="'+data.command_server_id+'"] .server-status');
			if (statusDict[data.status].name == 'success') {
				text = 'finished in '+data.time+' s';
				tclass = 'success';
			} else {
				text = 'failed with code '+data.return_code+' after '+data.time+' s';
				tclass = 'danger';
			}
			el.html(text).addClass('text-'+tclass);
		},
		command_started: function(data) {
			$('.server[data-command-server-id="'+data.command_server_id+'"]')
				.removeClass('text-muted')
				.parent().removeClass('text-muted');
		},
		execution_status: function(data) {
			executionStatus = statusDict[data.status].name;
			$('.execution-label').html(statusDict[data.status].label);
		},
		execution_started: function(data) {
			handlers.execution_status(data);
			$('.execution-time-start').html(data.time_start)
		},
		execution_completed: function(data) {
			handlers.execution_status(data);
			$('.execution-time-end').html(data.time_end).prev().show();
			$('.execution-time').html(data.time+' s');
			$('#execute-button').show();
		}
	};

	var lastId = 0,
		execution = $('#execution');
		executionId = execution.data('execution-id'),
		executionStatus = statusDict[execution.data('execution-status')].name,
		request = false,
		interval = false;
	interval = setInterval(function() {
		if (executionStatus == 'pending' || executionStatus == 'running') {
			if (!request) {
				request = true;
				$.get('/execution/live_log/'+executionId+'/'+lastId+'/', function (data, status, response) {
					var item;
					for (var i=0, n=data.length; i<n; i++) {
						item = data[i]
						console.log(item.event, item.data);
						if (item.event in handlers) {
							handlers[item.event](JSON.parse(item.data));
						}
						lastId = item.id;
					}
					request = false;
				});
			}
		} else {
			clearInterval(interval);
		}
	}, 1000);
})( jQuery );