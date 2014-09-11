class component::nginx {
  $app_name = hiera('application::name')
  $app_path = hiera('application::path')
  $run_path = hiera('application::run_path')
  $repository_path = hiera('application::repository_path')
  $log_path = hiera('application::log_path')
  $domain_name = hiera('application::domain_name')
   
  package { 'nginx':
    ensure => "latest"
  }

  service { 'nginx':
    ensure => running,
    enable => true,
    hasrestart => true,
    hasstatus  => true,
    require => [ Package['nginx'], File['django enable config'], File[$log_path] ],
  }

  file { '/etc/nginx/sites-enabled/default':
    ensure => absent,
    require => Package['nginx']
  }

  $vhost_path = "/etc/nginx/sites-available/${domain_name}"
  $cache_headers_enable = $::environment == 'production'
  $gzip_enable = $::environment == 'production'
  $static_only_collected = $::environment == 'production'
  file { 'django available config':
    path => $vhost_path,
    ensure => file,
    content => template("component/nginx.django.conf.erb"),
    require => Package['nginx'],
    notify => Service['nginx']
  } ->
  file { 'django enable config':
    path => "/etc/nginx/sites-enabled/${domain_name}",
    ensure => link,
    target => $vhost_path,
    require => [ File['django available config'] ], #, File['/etc/nginx/sites-enabled/']
  }

  #file { '/etc/nginx/sites-enabled/': 
  #  ensure  => 'directory', 
  #  recurse => true, 
  #  purge   => true, 
  #}
}