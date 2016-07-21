#!/bin/bash

apt-get install -y software-properties-common
apt-add-repository -y ppa:ansible/ansible
apt-get update
apt-get install -y ansible

# Install ansible roles
echo $role_list
for role in $role_list; do 
  ansible-galaxy install indigo-dc.$role;
done 
