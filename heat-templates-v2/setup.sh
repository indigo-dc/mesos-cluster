#!/bin/bash

MYIP=$(curl -s http://169.254.169.254/latest/meta-data/local-ipv4)
# Fix /etc/hosts
sed -i "s/127.0.1.1/$MYIP/" /etc/hosts

apt-get install -y software-properties-common
apt-add-repository -y ppa:ansible/ansible
apt-get update
apt-get install -y ansible
git clone https://github.com/indigo-dc/mesos-deploy.git /tmp/mesos-deploy
cp -r /tmp/mesos-deploy/ansible/* /etc/ansible/

