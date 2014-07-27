# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("1") do |config|
  config.vm.box = "opscode-ubuntu-13.10"
  config.vm.box_url = "http://opscode-vm-bento.s3.amazonaws.com/vagrant/virtualbox/opscode_ubuntu-13.10_chef-provisionerless.box"

  config.vm.host_name = "void"
#  config.vm.network :bridged

  config.vm.forward_port 80, 8080
  config.vm.forward_port 5432, 5432
  config.ssh.forward_agent = true

  config.vm.provision :shell, :path => "puppet/install.sh"

  config.vm.provision :puppet do |puppet|
    puppet.manifests_path = "puppet/manifests"
    puppet.module_path = "puppet/modules"
    puppet.manifest_file = "base.pp"
    puppet.options = "--hiera_config /vagrant/puppet/manifests/hiera.yaml"
    puppet.facter = {
        "environment" => "development",
    }
  end
end

Vagrant.configure("2") do |config|
  config.vm.provider :virtualbox do |vb|
    #vb.customize ["modifyvm", :id, "--cpuexecutioncap", "25"]
    vb.customize ["modifyvm", :id, "--memory", 1024]
    vb.customize ["modifyvm", :id, "--ioapic", "on"]
    vb.customize ["modifyvm", :id, "--cpus", "2"] 
  end
end
