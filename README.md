# Mesos Cluster 
> The present document describes how Apache Mesos is used by the [INDIGO-DataCloud](https://www.indigo-datacloud.eu/) PaaS layer. <br>
INDIGO-DataCloud (start date: 01/04/2015, end date: 30/09/2017) is a project funded under the Horizon2020 framework program of the European Union and led by the National Institute for Nuclear Physics (INFN). It developed a data and computing platform targeting scientific communities, deployable on multiple hardware and provisioned over hybrid (private or public) e-infrastructures. 
The INDIGO solutions are being evolved in the context of other European projects like [DEEP Hybrid-DataCloud](https://deep-hybrid-datacloud.eu), [eXtreme-DataCloud](http://www.extreme-datacloud.eu/) and [EOSC-Hub](https://www.eosc-hub.eu/)
<hr>

# Table of Contents

* [Introduction](#intro)
* [Features](#features)
  - [INDIGO Achievements](#indigo)
  - [DEEP Achievements](#deep)
* [Use-cases](#usecases)
* [Architecture](#architecture)
* [Releases](#releases)
* [Automated configuration with ansible playbook](#deploy-with-ansible)
* [Automated deployment (provisioning and configuration) with TOSCA](#deploy-with-tosca)
* [References](#references)



## <a id="intro">Introduction</a>

The **INDIGO-DataCloud PaaS** relies on [Apache Mesos](http://mesos.apache.org/) for:
- managed service deployment 
- user applications execution

The instantiation of the high-available Mesos cluster is managed by the INDIGO *[Orchestrator](https://www.gitbook.com/book/indigo-dc/orchestrator/details)* in a fully automated way as soon as a user request described by a TOSCA template is submitted. Once the cluster is up and running, it can be re-used for successive requests.

**Mesos** is able to manage cluster resources (cpu, mem) providing isolation and sharing across distributed applications (frameworks)

**[Marathon](https://mesosphere.github.io/marathon/)** and **[Chronos](https://mesos.github.io/chronos/)** are two powerful frameworks that can be deployed on top of a Mesos Cluster.

Sophisticated two-level scheduling and efficient resource isolation are the key-features of the Mesos middleware that are exploited in the INDIGO PaaS, in order to run different workloads (long-running services, batch jobs, etc) on the same resources while preserving isolation and prioritizing their execution.

**INDIGO** *PaaS* uses:
- Marathon to deploy, monitor and scale *Long-Running services*, ensuring that they are always up and running.
- Chronos to run *user applications* (jobs), taking care of fetching input data, handling dependencies among jobs, rescheduling failed jobs.


## <a id="features">Features</a>

- Automatic deployment through Ansible recipes embedded in TOSCA and HOT templates
  - All the services run in docker containers;
- High-availability of the cluster components: 
  - Leader election among master nodes managed by Zookeeper; 
  - HA Load-balancing;
-Service discovery through Consul that provides also DNS functionality and health checks; 
  - services are automatically registered in Consul as soon as they are deployed on the cluster
- The external access to the deployed services is ensured through load-balancers in HA (unique entrypoint: cluster Virtual IP)
- Cluster elasticity and application auto-scaling through CLUES plugin 
- GPU support

### <a id="indigo">INDIGO achievements</a>
- [Ansible roles](#ansible-roles) and [TOSCA templates](https://github.com/indigo-dc/tosca-templates/blob/master/mesos_cluster.yaml) for cluster set-up featuring high-availability, service-discovery and load-balancing; 
- Integration with the INDIGO [Orchestrator](https://www.gitbook.com/book/indigo-dc/orchestrator/details) 
  - Job submission and service deployment requests are described through TOSCA templates
- Definition of custom TOSCA [types](https://github.com/indigo-dc/tosca-types/blob/master/custom_types.yaml) for describing Chronos jobs and Marathon application  
- Cluster elasticity through [EC3/CLUES](https://github.com/indigo-dc/clues-indigo) plugin
- Zabbix monitoring [probes](https://github.com/indigo-dc/Monitoring) for Mesos, Marathon and Chronos;

### <a id="deep">DEEP achievements</a>
- The Ansible roles and TOSCA templates have been extended in order to support the usage of GPUs.

## <a id="usecases">Use-cases</a>
The INDIGO components developed for Mesos (ansible roles, docker images, tosca custom-types and templates) have been used to support different uses-cases:

- *Lifewatch-Algaebloom* for water quality modeling and analysis: 
  - [this TOSCA template](https://github.com/indigo-dc/tosca-templates/blob/master/lifewatch-algaebloom.yaml) can be used to run processing jobs on a Mesos cluster through the Chronos framework; 
- *Compact Muon Solenoid* (CMS) analysis cluster on-demand:
  - [this TOSCA template](https://github.com/indigo-dc/tosca-templates/blob/master/mesos_cluster_cms.yaml) can be used to deploy a complete cluster for the execution of HTCondor workload management system;
- *Dariah Zenodo-based* repository in the cloud using Marathon:
  - [this TOSCA template](https://github.com/indigo-dc/tosca-templates/blob/master/dariah_repository.yaml) can be used to deploy the DARIAH Zenodo-based repository in the cloud: all the services are run as Marathon apps.   


## <a id="architecture">Architecture</a>

The core components are:

- [Mesos](http://mesos.apache.org) cluster manager for efficient resource isolation and sharing across distributed services
- [Chronos](https://mesos.github.io/chronos/) a distributed task scheduler
- [Marathon](https://mesosphere.github.io/marathon) for cluster management of long running containerized services
- [ZooKeeper](https://zookeeper.apache.org/) used for leader election of the Mesos master, leader detection of the Mesos master by masters, agents and scheduler drivers, persisting Marathon/Chronos state information
- [Consul](http://consul.io) for service discovery
- [Docker](http://docker.io) container runtime
- [marathon-lb](https://github.com/mesosphere/marathon-lb) for managing HAProxy, by consuming Marathon's app state
- [Keepalived](http://www.keepalived.org/) used for the high-availability of the cluster load-balancers

These components are distributed on the cluster nodes as shown in the diagram below.

![alt mesoscluster](mesos-cluster-ha.png "INDIGO Mesos cluster architecture")

- **Master nodes** 
  - On every master node the following (dockerized) components run: zookeeper, mesos master, consul server, marathon, chronos   
- **Slave nodes**
  - On every slave node the following (dockerized) components run: mesos slave, consul agent
- **Load-balancers**
  - On the two load-balancers the following (dockerized) components run: keepalived and marathon-lb. keepalived ensures the high-availability of the load-balancer managing the cluster Virtual IP.

## <a id="releases">Releases</a>

| Release  | Component version |
| ------------- | ------------- |
| indigo_1  | Mesos 0.28.0 <br> Marathon 1.1.1 <br> Chronos 2.4.0 |
| indigo_2  | Mesos 1.1.0 <br> Marathon 1.4.1 <br> Chronos 3.0.2 |
| deep_1  | Mesos 1.5.0 <br> Marathon 1.5.6 <br> Chronos 3.0.2 patched for GPU support |

## <a id="deploy-with-ansible">Automated deployment with ansible playbook</a>

You can use this [guide](deploy/ansible/README.md) to deploy a Mesos cluster on a set of hosts using the following indigo-dc ansible roles:

- indigo-dc.zookeeper: 
  - source: https://github.com/indigo-dc/ansible-role-zookeeper
- indigo-dc.consul:
  - source: https://github.com/indigo-dc/ansible-role-consul
- indigo-dc.mesos:
  - source: https://github.com/indigo-dc/ansible-role-mesos
- indigo-dc.chronos:
  - source: https://github.com/indigo-dc/ansible-role-chronos
- indigo-dc.marathon:
  - source: https://github.com/indigo-dc/ansible-role-marathon
- indigo-dc.marathon-lb:
  - source: https://github.com/indigo-dc/ansible-role-marathon-lb
- indigo-dc.keepalived:
  - source: https://github.com/indigo-dc/ansible-role-keepalived

These ansible roles are published on Ansible Galaxy and can be installed through *ansible-galaxy* command: `ansible-galaxy install indigo-dc.rolename`

## <a id="deploy-with-tosca">Automated deployment (provisioning and configuration) with TOSCA</a>

You can use this [TOSCA template](https://github.com/indigo-dc/tosca-templates/blob/master/mesos_cluster.yaml) for setting up a complete Mesos cluster on Cloud resources.  


## <a id="references">References</a>
- **Apache mesos** 
  - Web site: http://mesos.apache.org/
  - Documentation: http://mesos.apache.org/documentation/latest/
  - Releases: http://mesos.apache.org/downloads/
  - Code repo: https://github.com/apache/mesos
  - Issue Tracker: https://issues.apache.org/jira/browse/MESOS

- **Marathon**
  - Web site: https://mesosphere.github.io/marathon/
  - Documentation: https://mesosphere.github.io/marathon/docs/
  - Releases: https://github.com/mesosphere/marathon/releases
  - Code repo: https://github.com/mesosphere/marathon
  - Issue Tracker: https://github.com/mesosphere/marathon/issues	

- **Chronos**
  - Web site: https://mesos.github.io/chronos/
  - Documentation: https://mesos.github.io/chronos/docs/
  - Releases: https://github.com/mesos/chronos/releases
  - Code repo: https://github.com/mesos/chronos
  - Issue tracker: https://github.com/mesos/chronos/issues

