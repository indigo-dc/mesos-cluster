## Instructions

<pre>
# git clone https://github.com/Cloud-PG/mesos-cluster.git
# cd mesos-cluster/heat-templates-v2
# vim env_heat
# heat stack-create -f mesoscluster-cms.yaml  -e env_heat CLUSTER_NAME
</pre>

In "env_heat" modify this parameters:
- `network` is the id of the Openstack network used in your project;
- `ssh_key_name` is the name of the ssh key to inject into your cluster machines;
- `master_flavor`, `loadbalancer_flavor` and `slave_flavor` are the names or ids of the flavors to be used to create the mesos master/slave/loadbalancer VMs;
- `number_of_slaves` and `number_of_masters` is the number of VMs to spawn;
- `server_image` is the name/id of the virtual image to be used to launch the VMs;
- `cms_*` are CMS specific parameters. `cms_local_site` has to start with the prefix `T3_IT_Opportunistic_`;
- `marathon_username` and `marathon_password` are the credentials that will be used to access Marathon endpoint;
- `iam_token` is the access token you can get through the `get_token.sh` script;

Note: you can omit master_flavor, slave_flavor and loadbalancer_flavor if your Openstack provides the "m1.small" flavor (this is the default provided in the template).

Most importantly you need to create and upload the Ubuntu 14.04 virtual image with heat hooks pre-installed (and provide its name or id in the parameter server_name unless you register it in glance with the default name used in the template "Ubuntu 14.04.3 LTS (HEAT)”).

You can create that image using this script that makes use of diskimage-builder: https://gist.github.com/maricaantonacci/5fba6a1e67eca9e3bdf2 
