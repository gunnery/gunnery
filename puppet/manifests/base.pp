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
#Exec["apt-update"] -> Package <| |>


include role::development
