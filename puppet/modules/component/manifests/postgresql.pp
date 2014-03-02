class component::postgresql {
  # class { 'postgresql::globals':
  #   manage_package_repo => true,
  #   version             => '9.1',
  # }->

  class { 'postgresql::server':
    #ip_mask_deny_postgres_user => '0.0.0.0/32',
    ip_mask_allow_all_users    => '0.0.0.0/0',
    listen_addresses           => '*',
    ipv4acls                   => [
    	'host gunnery gunnery 192.168.0.0/24 md5'
    	],
    #manage_firewall            => true,
    postgres_password          => 'postgres',
  }

  postgresql::server::db { 'gunnery':
    user     => 'gunnery',
    password => postgresql_password('gunnery', 'gunnery'),
  }
}