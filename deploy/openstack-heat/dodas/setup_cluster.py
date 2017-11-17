#! /usr/bin/python
"""
Script to launch a cluster deployment in
"""
from __future__ import print_function
import argparse
import getpass
import json

import yaml
from keystoneauth1 import loading, session

from heatclient import client
from datetime import date

AUTH_URL = ""
PROJECT_ID = ""
VERIFY_CA = False

assert AUTH_URL != "", "[Error]==> You have to set 'AUTH_URL' variable"
assert PROJECT_ID != "", "[Error]==> You have to set 'PROJECT_ID' variable"

try:
    USER = str(raw_input('Username:'))
    print("|->: {}".format(USER))
except ValueError:
    print("Not a str")

PASSWD = getpass.getpass('Password:')
LOADER = loading.get_plugin_loader('password')

AUTH = LOADER.load_from_options(
    auth_url=AUTH_URL,
    username=USER,
    password=PASSWD,
    project_id=PROJECT_ID,
    user_domain_name='default'
)

if VERIFY_CA:
    SESS = session.Session(auth=AUTH,
                           verify='ca.pem')
else:
    SESS = session.Session(auth=AUTH)

print("[Token]==>", SESS.get_token())
try:
    STK_NAME = str(raw_input('Stack name:'))
    print("|->: {}".format(STK_NAME))
except ValueError:
    print("Not a str")


HEAT = client.Client('1', session=SESS)


def purge_yaml(data):
    """Checks and converts data in basic types."""
    basic_types = [int, float, str, unicode, list]
    for key, value in data.items():
        if isinstance(value, dict):
            purge_yaml(value)
        elif isinstance(value, date):
            data[key] = value.isoformat()
        elif not any([isinstance(value, type_) for type_ in basic_types]):
            raise Exception(
                "!!!Warning!!! '{}' not recognized. [{}]->[{}]".format(
                    type(value), key, value)
            )

with open('env_heat.json') as data_file:
    ENV = json.load(data_file)

with open('../setup.sh') as data_file:
    SETUP = data_file.read()

HEAT.stacks.create(stack_name=STK_NAME,
                   template_url='https://raw.githubusercontent.com/indigo-dc/mesos-cluster/master/deploy/openstack-heat/dodas/mesoscluster-cms.yaml',
                   environment=ENV,
                   files={'https://raw.githubusercontent.com/indigo-dc/mesos-cluster/master/deploy/openstack-heat/setup.sh': SETUP})
