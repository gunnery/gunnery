class component::celery {
  $user = hiera('application::user')
  $app_name = hiera('application::name')
  $app_path = hiera('application::path')
  $log_path = hiera('application::log_path')
  $run_path = hiera('application::run_path')
  $secure_path = hiera('application::secure_path')
  $virtualenv_path = hiera('application::virtualenv_path')
  $workers = hiera('celery::workers')
  $concurrency = hiera('celery::concurrency')
  $secret_key = hiera('application::secret_key')
  $environment = $::environment

  package {'celery':
    provider => pip,
    ensure => present,
  }

  user { $user:
    ensure => present,
  } ->
  file { "/home/$user":
    ensure => directory,
    owner => $user,
    group => $user,
    mode => 700,
  }

  file { '/etc/default/celeryd':
    ensure => file,
    content => template("component/celery.default.erb"),
    notify => Service["celeryd"],
    owner => $user,
    group => $user,
    mode => 700,
  }

  file { '/etc/init.d/celeryd':
    ensure => file,
    mode => 755,
    source => "puppet:///modules/component/celery.initd",
    notify => [ Service["celeryd"], Exec['update-rc.d celeryd defaults'] ]
  }

  exec { 'update-rc.d celeryd defaults':
    refreshonly => true
  }

  service { 'celeryd':
    ensure => running,
    enable => true,
    hasrestart => true,
    hasstatus  => true,
    require => [ 
      File['/etc/init.d/celeryd'], 
      File['/etc/default/celeryd'], 
      User[$user],
      Class["component::virtualenv"] ]
  }
}