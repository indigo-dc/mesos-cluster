#! /usr/bin/python
"""
Script to launch a cluster deployment in 
"""
from keystoneauth1 import loading
from keystoneauth1 import session
from heatclient import client
from yaml import load, dump
import json

import argparse
import getpass


try:
    user=str(raw_input('Username:'))
except ValueError:
    print "Not a str"

passwd = getpass.getpass('Password:')
loader = loading.get_plugin_loader('password')

auth = loader.load_from_options(auth_url='CHANGE ME', 
                                username=user, 
                                password=passwd, 
                                project_id='CHANGE ME',
                                user_domain_name ='default')

sess = session.Session(auth=auth)
print("Token:",sess.get_token())
try:
    stk_name=str(raw_input('Stack name:'))
except ValueError:
    print "Not a str"


heat = client.Client('1', session=sess)

stream = file('mesoscluster-cms.yaml', 'r')
data = load(stream)
data = json.dumps(data,indent=4, sort_keys=True, default=str)
data = json.loads(data)

with open('env_heat.json') as data_file:    
    env_ = json.load(data_file)

with open('setup.sh') as data_file:
    setup = data_file.read()

heat.stacks.create(stack_name=stk_name,
		   template=data, 
                   environment=env_,
                   files={'https://raw.githubusercontent.com/indigo-dc/mesos-cluster/master/deploy/openstack-heat/setup.sh': setup})
