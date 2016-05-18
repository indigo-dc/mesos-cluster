#!/bin/bash

MYIP=$(curl -s http://169.254.169.254/latest/meta-data/local-ipv4)
# Fix /etc/hosts
sed -i "s/127.0.1.1/$MYIP/" /etc/hosts

apt-get install -y software-properties-common
apt-add-repository -y ppa:ansible/ansible
apt-get update
apt-get install -y ansible

# Install ansible roles
echo $role_list
for role in $role_list; do 
  ansible-galaxy install indigo-dc.$role;
done 
