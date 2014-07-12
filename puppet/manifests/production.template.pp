stage { 'setup':
	before => Stage['main'],
}
class setup {
	include locales
}
class { 'setup':
	stage => setup
}

Exec {
	path => '/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin',
	logoutput => "on_failure"
}
exec { 'apt-update':
	command => 'apt-get update',
	returns => [0, 100],
}
Exec["apt-update"] -> Package <| |>


/** example 3 node setup */
node 'app01' {
	include role::production::frontend
}

node 'ds01' {
	include role::production::datastore
}

node 'backend01' {
	include role::production::backend
}