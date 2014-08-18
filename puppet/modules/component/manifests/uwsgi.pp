class component::uwsgi {
  $user = hiera('application::user')
  $app_name = hiera('application::name')
  $domain_name = hiera('application::domain_name')
  $app_path = hiera('application::path')
  $log_path = hiera('application::log_path')
  $run_path = hiera('application::run_path')
  $virtualenv_path = hiera('application::virtualenv_path')
  $secret_key = hiera('application::secret_key')
  $environment = $::environment
  
  service { 'uwsgi':
    ensure => running,
    enable => true,
    hasrestart => true,
    hasstatus  => true,
    require => [ File['sites-enabled config'], Class["component::virtualenv"] ]
  }
  
  # Prepare directories
  file { ['/etc/uwsgi', '/etc/uwsgi/sites-available', '/etc/uwsgi/sites-enabled']: 
    ensure => directory,
    require => Class["component::virtualenv"],
    before => File['sites-available config'],
    recurse => true, 
  }
  
  # Upstart file
  file { '/etc/init.d/uwsgi':
    ensure => file,
    content => template("component/uwsgi.erb"),
    require => Class["component::virtualenv"],
    mode => 0744
  }
  
  # Vassals ini file
  file { 'sites-available config':
    path => "/etc/uwsgi/sites-available/${domain_name}.ini",
    ensure => file,
    mode => 0700,
    owner => $user,
    group => $user,
    content => template("component/uwsgi.ini.erb"),
    notify => Service['uwsgi']
  }
  
  file { 'sites-enabled config':
    path => "/etc/uwsgi/sites-enabled/${domain_name}.ini",
    ensure => link,
    target => "/etc/uwsgi/sites-available/${domain_name}.ini",
    require => File['sites-available config']
  }
  
}
