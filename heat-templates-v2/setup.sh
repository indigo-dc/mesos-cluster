#!/bin/bash

apt-get install -y software-properties-common
apt-add-repository -y ppa:ansible/ansible
apt-get update
apt-get install -y ansible

#apt-get install -y python-paramiko python-netaddr
#wget http://launchpadlibrarian.net/291371956/ansible_2.1.1.0-1~ubuntu16.04.1_all.deb
#dpkg -i ansible_2.1.1.0-1~ubuntu16.04.1_all.deb
#rm ansible_2.1.1.0-1~ubuntu16.04.1_all.deb

# Install ansible roles
echo $role_list
for role in $role_list; do 
  if [ "$role" == "mesos-rexray" ]; then
     git clone https://github.com/indigo-dc/ansible-role-mesos.git -b enable_dvdi_mod /etc/ansible/roles/indigo-dc.mesos
  else
     ansible-galaxy install indigo-dc.$role;
  fi
done 
