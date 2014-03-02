class profile::backend {
	include component::common
	include component::application
	include component::celery
}

class profile::frontend {
	include component::common
	include component::application
	include component::nginx
	include component::uwsgi
}

class profile::datastore {
	include component::common
	include component::rabbitmq
	include component::postgresql
}