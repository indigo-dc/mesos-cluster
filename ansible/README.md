Ansible roles to deploy a mesos cluster with Marathon and Chronos framework.

Service-discovery and load-balancing ensured by Consul, dnsmasq, mesos-consul, marathon-consul, haproxy-consul.

Marathon and Chronos endpoints are SSL-enabled with HTTP basic authentication (username/password).

## Dependencies
Ubuntu 14.04
ansible >= 2.0
(tested with ansible 2.0)


## Roles
- docker (`roles/docker`): install docker-py version=1.2.3 using pip and docker-engine from docker apt repo
- zookepeer (`roles/zookeeper`): configure and start zookeeper container
- mesos (`roles/mesos`): configure and start containers for mesos master (`when: mesos_install_mode=master`) and/or mesos slave (`when: mesos_install_mode=slave`) 
- marathon (`roles/marathon`): configure and start container for marathon framework

## Example playbook

See `site.yml`
