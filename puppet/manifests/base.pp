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

include profile::datastore
include profile::backend
include profile::frontend

if $environment == 'development' {
  $app_name = hiera('application::name')
  $user = hiera('application::user')
  $secret_key = hiera('application::secret_key')
  $virtualenv_path = hiera('application::virtualenv_path')
  file { "/home/${user}/.bash_profile":
    ensure => file,
    content => template("component/bash_profile.erb"),
    owner => $user,
    group => $user,
    mode => 700,
  }
}