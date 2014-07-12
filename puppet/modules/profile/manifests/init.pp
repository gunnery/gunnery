class profile {
	include component::common
}

class profile::backend inherits profile {
	include component::application
	include component::celery
}

class profile::frontend inherits profile {
	include component::application
	include component::nginx
	include component::uwsgi
}

class profile::datastore inherits profile {
	include component::rabbitmq
	include component::postgresql
}