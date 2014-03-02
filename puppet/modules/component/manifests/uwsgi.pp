class component::uwsgi {
  $user = hiera('application::user')
  $app_name = hiera('application::name')
  $domain_name = hiera('application::domain_name')
  $app_path = hiera('application::path')
  $log_path = hiera('application::log_path')
  $run_path = hiera('application::run_path')
  $virtualenv_path = hiera('application::virtualenv_path')
  $environment = $::environment
  
  service { 'uwsgi':
    ensure => running,
    enable => true,
    hasrestart => true,
    hasstatus  => true,
    require => [ File['apps-enabled config'], Class["component::virtualenv"] ]
  }
  
  # Prepare directories
  file { ['/etc/uwsgi', '/etc/uwsgi/apps-available', '/etc/uwsgi/apps-enabled']: 
    ensure => directory,
    require => Class["component::virtualenv"],
    before => File['apps-available config'],
    recurse => true, 
    purge   => true, 
  }
  
  # Upstart file
  file { '/etc/init.d/uwsgi':
    ensure => file,
    content => template("component/uwsgi.erb"),
    require => Class["component::virtualenv"],
    mode => 0744
  }
  
  # Vassals ini file
  file { 'apps-available config':
    path => "/etc/uwsgi/apps-available/${domain_name}.ini",
    ensure => file,
    content => template("component/uwsgi.ini.erb"),
    notify => Service['uwsgi']
  }
  
  file { 'apps-enabled config':
    path => "/etc/uwsgi/apps-enabled/${domain_name}.ini",
    ensure => link,
    target => "/etc/uwsgi/apps-available/${domain_name}.ini",
    require => File['apps-available config']
  }
  
}
