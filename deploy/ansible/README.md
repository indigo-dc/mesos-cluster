Ansible roles to deploy a mesos cluster with Marathon and Chronos framework.

Service-discovery and load-balancing ensured by Consul, dnsmasq, marathon-lb.

Marathon and Chronos endpoints are SSL-enabled with HTTP basic authentication (username/password).

## Dependencies
Ubuntu 16.04
ansible >= 2.0
(tested with ansible >= 2.5)


## Usage

Clone the `mesos-cluster` repository

```
git clone https://github.com/indigo-dc/mesos-cluster.git
cd mesos-cluster/deploy/ansible
```

Edit the `inventory` file: replace the IPs with the address of your hosts and set the variables
````
[mesos_masters]
172.30.6.129
172.30.6.130
172.30.6.131

[mesos_slaves]
172.30.6.132
172.30.6.133
172.30.6.134

[load_balancers]
172.30.6.135
172.30.6.136

### You can leave untouched the following groups. Go to the variables section below.

[marathon_servers:children]
mesos_masters

[zookeeper_servers:children]
mesos_masters

[chronos_servers:children]
mesos_masters

[consul_servers:children]
mesos_masters


### Set variables
[all:vars]
mesos_username="admin"
mesos_password="changeit"
marathon_username="admin"
marathon_password="changeit"
chronos_username="admin"
chronos_password="changeit"

[load_balancers:vars]
keepalived_virtual_ip="172.30.6.137"
````

Install the depedencies:
```
ansible-playbook install -r requirements.yml
```


Run the playbook:
````
ansible-playbook -i inventory site.yml
````


## Main Roles
- indigo-dc.docker: install docker-ce and configure the daemon
- indigo-dc.zookepeer: configure and start zookeeper container
- indigo-dc.mesos: configure and start containers for mesos master (`when: mesos_install_mode=master`) and/or mesos slave (`when: mesos_install_mode=slave`) 
- indigo-dc.marathon: configure and start container for marathon framework

