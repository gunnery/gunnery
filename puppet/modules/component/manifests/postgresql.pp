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

  $database_user = hiera('postgresql::user')
  $database_name = hiera('postgresql::name')
  $database_password = hiera('postgresql::password')
  postgresql::server::db { $database_name:
    user     => $database_user,
    password => postgresql_password($database_user, $database_password),
  }
}