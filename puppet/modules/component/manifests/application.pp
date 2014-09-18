class component::application {
  $user = hiera('application::user')
  $app_name = hiera('application::name')
  $secret_key = hiera('application::secret_key')
  $log_path = hiera('application::log_path')
  $app_path = hiera('application::path')
  $virtualenv_path = hiera('application::virtualenv_path')
  $environment = $::environment

  include python::dev
  package {['bpython', "git-core", "vim"]:
    ensure => 'latest'}

  file { [
      hiera('application::root_path'),
      hiera('application::run_path')
    ]:
    ensure => directory,
    owner => $user,
    group => $user,
    mode => 755,
  } ->
  file { [
      $log_path,
      hiera('application::secure_path')
    ]:
    ensure => directory,
    owner => $user,
    group => $user,
    mode => 700,
  } -> class { 'component::virtualenv': }

  file { "/home/${user}/.bash_profile":
    ensure => file,
    content => template("component/bash_profile.erb"),
    owner => $user,
    group => $user,
    mode => 700,
  }
}

class component::virtualenv () {
  $user = hiera('application::user')
  $app_path = hiera('application::path')
  $requirements_path = hiera('application::requirements_path')
  $virtualenv_path = hiera('application::virtualenv_path')

  class { "python::venv":
    owner => $user,
    group => $user,
    notify => Exec['chownvenv']
  }
  class { 'postgresql::lib::devel': }->
  python::venv::isolate { $virtualenv_path:
    requirements => $requirements_path,
    notify => Exec['chownvenv']
  }

  exec {'chownvenv':
    refreshonly => true,
    command => "chown -R ${user}:${user} ${virtualenv_path}"
  }
}
