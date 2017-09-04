#! /usr/bin/python
from keystoneauth1 import loading
from keystoneauth1 import session
from keystoneclient.v3 import client
from heatclient import client
from yaml import load, dump
import json

import argparse
import getpass


try:
    user=str(raw_input('Username:'))
except ValueError:
    print "Not a str"

try:
    proj_id=str(raw_input('Project id:'))
except ValueError:
    print "Not a str"

passwd = getpass.getpass('Password:')



loader = loading.get_plugin_loader('password')
auth = loader.load_from_options(auth_url='http://openstack.fisica.unipg.it:5000/v3', 
                                username=user, 
                                password=passwd, 
                                project_id=proj_id,
                                user_domain_name ='default')

sess = session.Session(auth=auth)
print("Token:",sess.get_token())

heat = client.Client("1", session=sess)

try:
    stk_name=str(raw_input('Stack name:'))
except ValueError:
    print "Not a str"

stream = file('mesoscluster-cms.yaml', 'r')
data = load(stream)
data = json.dumps(data,indent=4, sort_keys=True, default=str)
data = json.loads(data)

try:
    env_h=str(raw_input('Path to a json env_heat:'))
except ValueError:
    print "Not a str"

with open(env_h) as data_file:    
    env_ = json.load(data_file)

with open('setup.sh') as data_file:
    setup = data_file.read()

heat.stacks.create(stack_name=stk_name,
		   template=data, 
                   environment=env_,
                   files={'https://raw.githubusercontent.com/Cloud-PG/mesos-cluster/devel/heat-templates-v2/setup.sh': setup})
