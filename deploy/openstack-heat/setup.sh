#!/bin/bash

#Remove old ansible as workaround for https://github.com/ansible/ansible-modules-core/issues/5144
dpkg -r ansible
apt-get autoremove -y

#install ansible 2.2.1 (version used in INDIGO)
apt-get update
apt-get install -y python-pip python-dev libffi-dev libssl-dev #https://github.com/geerlingguy/JJG-Ansible-Windows/issues/28
pip install ansible==2.2.1

# workaround for https://github.com/ansible/ansible/issues/20332
sed -i 's:#remote_tmp:remote_tmp:' /etc/ansible/ansible.cfg

# Install ansible roles
echo $role_list
IFS=','
###########################################
# NOTE: you can test a feature branch for #
# ansible roles using git clone instead   #
# of ansible-galaxy as follows:           #
###########################################
for role in $role_list; do 
     ansible-galaxy install indigo-dc.$role;
done

###########################################
# NOTE: you can test a feature branch for #
# ansible roles using git clone instead   #
# of ansible-galaxy as follows:           #
###########################################
#
# for role in $role_list; do
#   if [ "$role" == "mesos" ]; then
#     git clone https://github.com/indigo-dc/ansible-role-mesos.git -b enable_dvdi_mod /etc/ansible/roles/indigo-dc.mesos
#   elif [ "$role" == "cms_config" ]; then
#     git clone https://github.com/indigo-dc/ansible-role-cms_config.git -b new_proxy /etc/ansible/roles/indigo-dc.cms_config
#   else
#     ansible-galaxy install indigo-dc.$role;
#   fi
# done
