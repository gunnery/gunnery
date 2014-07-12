class role::development {
	include profile::datastore
	include profile::backend
	include profile::frontend
}

class role::production::frontend {
	include profile::frontend
}

class role::production::backend {
	include profile::backend
}

class role::production::datastore {
	include profile::datastore
}