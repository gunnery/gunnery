#!/bin/bash -e
version=`puppet -V`
[ "${version:0:1}" == "3" ] && exit 0
echo "install puppet 3"
if [ ! -e "/etc/apt/sources.list.d/puppetlabs.list" ]; then
	echo "add apt source list"
	DEB="puppetlabs-release-stable.deb"
	wget -q "http://apt.puppetlabs.com/${DEB}"
	dpkg -i "${DEB}" >/dev/null
fi
apt-get update >/dev/null
apt-get install -y puppet >/dev/null