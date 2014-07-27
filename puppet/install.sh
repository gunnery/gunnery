#!/bin/bash -e

if hash puppet 2>/dev/null ; then
	version=`puppet -V`
	[ "${version:0:1}" == "3" ] && exit 0
fi


if [ ! -e "/etc/apt/sources.list.d/puppetlabs.list" ]; then
	echo "add apt source list"
	DEB="puppetlabs-release-stable.deb"
	wget -q "http://apt.puppetlabs.com/${DEB}"
	dpkg -i "${DEB}" >/dev/null
fi
echo "install puppet 3"
apt-get update >/dev/null
apt-get install -y --force-yes puppet >/dev/null