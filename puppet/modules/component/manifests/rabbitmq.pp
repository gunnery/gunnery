class component::rabbitmq {
  package { 'rabbitmq-server':
    ensure => latest
  }
  
  service { 'rabbitmq-server':
    ensure => running,
    enable => true,
    require => [ Package['rabbitmq-server'] ]
  }
}