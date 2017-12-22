#-*- coding: utf-8 -*-
#! /usr/bin/python
"""
Script to launch a cluster deployment in
"""
from __future__ import print_function

import argparse
import getpass
import json
from datetime import date
from os import path
from sys import argv, exit, stdout
from time import sleep

import requests
import yaml
from keystoneauth1 import loading, session
from keystoneauth1 import exceptions as keystone_exc

from heatclient import client


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


SPINNER = ['|', '/', '—', '\\']


def get_stack(heat, stk_name, monitor=True):
    """Select a stack."""
    cur_stack_list = list(heat.stacks.list())
    for stack in cur_stack_list:
        if stack.stack_name == stk_name:
            return stack

    if not monitor:
        print(bcolors.HEADER +
              "!!!===>[STACK NOT EXISTS ANYMORE]<===!!!" + bcolors.ENDC)
        exit(0)
    else:
        print(bcolors.FAIL + "!!!===>[STACK NOT EXISTS]<===!!!" + bcolors.ENDC)
        exit(-1)


def purge_yaml(data):
        """Checks and converts data in basic types."""
        basic_types = [int, float, str, unicode, list]
        for key, value in data.items():
            if isinstance(value, dict):
                purge_yaml(value)
            elif isinstance(value, date):
                data[key] = value.isoformat()
            elif value and not any([isinstance(value, type_) for type_ in basic_types]):
                raise Exception(
                    "!!!Warning!!! '{}' not recognized. [{}]->[{}]".format(
                        type(value), key, value)
                )


def main():

    parser = argparse.ArgumentParser(
        prog='setup_cluster.py', argument_default=argparse.SUPPRESS)

    parser.add_argument('config_file', metavar="filename",
                        default=None, help='Cluster setup configuration file')
    parser.add_argument('--auth-url', default=None,
                        help='Override URL endpoint for AUTH of config file')
    parser.add_argument('--project-id', default=None,
                        help='Override Openstack project ID of config file')
    parser.add_argument('--user', default=None,
                        help='Override Openstack user of config file')
    parser.add_argument('--stack-name', default=None,
                        help='Override Openstack stack name of config file')
    parser.add_argument('--heat-template', default=None,
                        help='Override HEAT template file of config file')
    parser.add_argument('--heat-environment-variables', default=None,
                        help='Override HEAT environment variables file of config file')
    parser.add_argument('--setup-script', default=None,
                        help='Override setup script file of config file')

    # parser.add_argument('run', nargs='?', default="run", help='Run the setup
    # of the given configuration')

    subparsers = parser.add_subparsers(help='Cluster setup commands')

    parser_run = subparsers.add_parser(
        'run', help='Run the setup of the given configuration')
    parser_run.set_defaults(debug=False, cmd="run")
    parser_run.add_argument(
        '--new-access-token', default='True', choices=['True', 'False'],
                        help='Request an access token with the user data config file')

    parser_delete = subparsers.add_parser(
        'delete', help='Delete cluster with the given configuration')
    parser_delete.set_defaults(debug=False, cmd="delete")

    parser_status = subparsers.add_parser(
        'status', help='Get the cluster status with the given configuration')
    parser_status.set_defaults(debug=False, cmd="status")
    parser_status.add_argument(
        '--monitor', default='False', choices=['True', 'False'],
                        help='Shows the status of the cluster during the setup')

    parser_debug = subparsers.add_parser(
        'debug', help='Debug the given configuration')
    parser_debug.set_defaults(debug=True, cmd="run")
    subparsers_debug = parser_debug.add_subparsers(help='Debug commands')

    parser_resources = subparsers_debug.add_parser(
        'resources', help='Command to execute as resource query')
    parser_resources.set_defaults(query="resources")
    parser_resources.add_argument(
        'resource_command', metavar="command", nargs='?', default="fails",
                                  type=str, help='Command to execute with heat resources. Possible values:["fails", "all"]')

    parser_softwares = subparsers_debug.add_parser(
        'softwares', help='Command to execute as resource query')
    parser_softwares.set_defaults(query="softwares")
    parser_softwares.add_argument(
        'software_command', metavar="command", nargs='?', default="fails",
                                 type=str, help='Command to execute with heat softwares. Possible values:["fails", "all", ID]')

    args, _ = parser.parse_known_args()

    # Open config file
    with open(args.config_file) as config_file:
        config = json.load(config_file)

    # Override config file fields if needed
    for key, value in vars(args).items():
        if key in config and value is not None:
            config[key] = value

    OPENSTACK_AUTH_URL = config.get('openstack_auth_url')
    OPENSTACK_PROJECT_ID = config.get('openstack_project_id')

    assert OPENSTACK_AUTH_URL != "", "[Error]==> You have to set 'OPENSTACK_AUTH_URL' variable"
    assert OPENSTACK_PROJECT_ID != "", "[Error]==> You have to set 'OPENSTACK_PROJECT_ID' variable"

    try:
        #
        # Use command line input
        # USER = str(raw_input('Username:'))
        OPENSTACK_USER = config.get('openstack_user')
        print(bcolors.HEADER +
              "[User]==>" + bcolors.OKGREEN + "{}".format(OPENSTACK_USER) + bcolors.ENDC)
    except ValueError:
        print("Not a str")

    PASSWD = getpass.getpass(bcolors.WARNING + '[Insert Password]:' + bcolors.ENDC)

    print(bcolors.HEADER + "[Password]==>" + bcolors.WARNING + "{}".format(
        ''.join('*' for _ in range(len(PASSWD)))) +
        bcolors.ENDC
    )
    #
    LOADER = loading.get_plugin_loader('password')

    AUTH = LOADER.load_from_options(
        auth_url=OPENSTACK_AUTH_URL,
        username=OPENSTACK_USER,
        password=PASSWD,
        project_id=OPENSTACK_PROJECT_ID,
        user_domain_name='default'
    )

    try:
        SESS = session.Session(auth=AUTH)
        print(bcolors.HEADER + "[Token Openstack]==>" + bcolors.OKBLUE + SESS.get_token() + bcolors.ENDC)
    except keystone_exc.http.Unauthorized:
        print(bcolors.FAIL + "[ERROR]==> Login failed! You're not authorized..." + bcolors.ENDC)
        exit(1)

    try:
        # STK_NAME = str(raw_input('Stack name:'))
        #
        # DEV
        STK_NAME = config.get('stack_name')
        print(bcolors.HEADER + "[STACK NAME]==>" +
              bcolors.WARNING + "{}".format(STK_NAME) + bcolors.ENDC)
        #
        # print("|->: {}".format(STK_NAME))
    except ValueError:
        print("Not a str")

    HEAT = client.Client('1', session=SESS)

    with file(config.get('heat_template'), 'r') as yaml_file:
        DATA = yaml.safe_load(yaml_file)
        purge_yaml(DATA)

    heat_environment_vars = config.get('heat_environment_variables', False)

    if heat_environment_vars:
        _, extension = path.splitext(heat_environment_vars)
        with open(heat_environment_vars) as data_file:
            if extension == ".json":
                ENV = json.load(data_file)
            elif extension == ".yaml":
                ENV = yaml.safe_load(data_file)
                purge_yaml(ENV)
            else:
                raise Exception(
                    "'{}' extension is not valid for an heat environment variable file.".format(extension))

    # RUN
    if args.cmd == "run":
        # CREATE CLUSTER (RUN NOT DEBUG)
        if not args.debug:
            # INDIGO ACCESS TOKEN
            if config.get('indigo_iam', False):
                # NEW ACCES TOKEN
                if args.new_access_token == 'True':
                    INDIGO_PASSWD = getpass.getpass(
                        bcolors.WARNING + '[Insert INDIGO Password]:' + bcolors.ENDC)
                    indigo_iam_data = config.get('indigo_iam')
                    indigo_url = indigo_iam_data.pop('url')
                    indigo_iam_data['password'] = INDIGO_PASSWD
                    res = requests.post(
                        indigo_url,
                        data=indigo_iam_data
                    )
                    if res.status_code == 200:
                        access_token = json.loads(
                            res.content).get('access_token')
                        with open(".access_token", "w") as access_token_file:
                            access_token_file.write(res.content)
                    else:
                        raise Exception(
                            "Error during access token request.\n==> Status code {}\n==>Content\n{}".format(res.status_code, res.content))
                else:
                    try:
                        with open(".access_token") as access_token_file:
                            access_token = json.load(
                                access_token_file).get('access_token')
                    except IOError:
                        raise Exception(
                            "File '.access_token' not exists. You have to request a new access token!")

                ENV['parameters']['iam_token'] = access_token

                print(bcolors.HEADER + "[ACCESS TOKEN]==>" + bcolors.OKBLUE + ENV[
                    'parameters']['iam_token'] + bcolors.ENDC)

            files = {}
            for openstack_filename, file_path in config.get('files', {}).items():
                with open(file_path) as data:
                    files[openstack_filename] = data.read()

            stack = HEAT.stacks.create(
                stack_name=STK_NAME,
                template=DATA,
                environment=ENV,
                files=files
            )

            print(bcolors.OKGREEN + "![STACK CREATED]!->" + bcolors.HEADER + stack[
                  'stack']['id'] + bcolors.ENDC)
        # RUN DEBUG
        elif args.debug:
            # Check logs
            cur_stack = get_stack(HEAT, STK_NAME)
            # DEBUG RESOURCES
            if args.query == "resources":
                # Get resources
                resources = HEAT.resources.list(stack_id=cur_stack.id)

                print(bcolors.HEADER + "=>[HEAT RESOURCES]" + bcolors.ENDC)
                for resource in sorted(resources, key=lambda elm: elm.resource_type):
                    # print(dir(resource), json.dumps(resource._info,
                    # indent=2))
                    if args.resource_command == "fails":
                        if resource.resource_status == "CREATE_FAILED":
                            print("[{}]=>({})[\033[91mname=\033[0m{}][\033[91mtype=\033[0m{}][\033[91mstatus-reason=\033[0m{}]".format(
                                bcolors.OKBLUE +
                                    resource.resource_status + bcolors.ENDC,
                                bcolors.HEADER +
                                    resource.physical_resource_id +
                                        bcolors.ENDC,
                                bcolors.OKGREEN +
                                    resource.resource_name + bcolors.ENDC,
                                bcolors.OKGREEN +
                                    resource.resource_type + bcolors.ENDC,
                                bcolors.OKGREEN +
                                    resource.resource_status_reason
                            ))
                    elif args.resource_command == "all":
                        print("[{}]=>({})[\033[91mname=\033[0m{}][\033[91mtype=\033[0m{}][\033[91mstatus-reason=\033[0m{}]".format(
                            bcolors.OKBLUE +
                                    resource.resource_status + bcolors.ENDC,
                                bcolors.HEADER +
                                    resource.physical_resource_id +
                                        bcolors.ENDC,
                                bcolors.OKGREEN +
                                    resource.resource_name + bcolors.ENDC,
                                bcolors.OKGREEN +
                                    resource.resource_type + bcolors.ENDC,
                                bcolors.OKGREEN +
                                    resource.resource_status_reason +
                                        bcolors.ENDC
                        ))
                    else:
                        raise Exception("No valid command for resources")
                print(bcolors.HEADER + "=>[END HEAT RESOURCES]" + bcolors.ENDC)
            # DEBUG SOFTWARES
            elif args.query == "softwares":
                # Get softwares
                softwares = list(HEAT.software_deployments.list())

                print(bcolors.HEADER + "=>[HEAT SOFTWARES]" + bcolors.ENDC)
                for software in softwares:
                    if args.software_command == "fails":
                        if software.status == "FAILED":
                            print("[{}]=>({})".format(
                                bcolors.OKBLUE +
                                        software.status + bcolors.ENDC,
                                    bcolors.HEADER + software.id + bcolors.ENDC
                            ))
                    elif args.software_command == "all":
                        print("[{}]=>({})".format(
                            bcolors.OKBLUE +
                                    software.status + bcolors.ENDC,
                                bcolors.HEADER + software.id + bcolors.ENDC
                        ))
                    elif args.software_command == software.id:
                        print("[{}]=>({})".format(
                            bcolors.OKBLUE +
                                    software.status + bcolors.ENDC,
                                bcolors.HEADER + software.id + bcolors.ENDC
                        ))
                        for key, value in software.output_values.items():
                            print(bcolors.WARNING + "==>[{}]".format(
                                key) + bcolors.ENDC, end="")
                            try:
                                tmp = json.loads(value)
                                print(json.dumps(tmp, indent=2))
                            except (ValueError, TypeError) as err:
                                print(
                                    bcolors.OKBLUE + "[It's not JSON data]" + bcolors.ENDC)
                                if isinstance(value, str):
                                    print("\n".join(value.split("\\n")))
                                else:
                                    print(value)
                            print(
                                bcolors.WARNING + "==>[END({})]\n".format(key) + bcolors.ENDC)
                print(bcolors.HEADER + "=>[END HEAT SOFTWARES]" + bcolors.ENDC)
    # DELETE
    elif args.cmd == "delete":
        cur_stack = get_stack(HEAT, STK_NAME, False)
        cur_stack.delete()
        print(bcolors.HEADER + "[STACK DELETE]==>" +
              bcolors.FAIL + "In progress" + bcolors.ENDC, end="\r")

        cur_stack = get_stack(HEAT, STK_NAME, False)

        idx = 0
        while cur_stack.stack_status == "DELETE_IN_PROGRESS":
            cur_stack = get_stack(HEAT, STK_NAME, False)
            print(bcolors.HEADER + "[STACK DELETE]==>" +
                  bcolors.FAIL + "In progress [" + SPINNER[idx] + "]" + bcolors.ENDC, end="\r")
            stdout.flush()
            idx = (idx + 1) % len(SPINNER)
            sleep(1)
    # STATUS
    elif args.cmd == "status":
        cur_stack = get_stack(HEAT, STK_NAME)

        if args.monitor == 'False':
            print(bcolors.HEADER + "[STACK STATUS]==>" + bcolors.WARNING + "{}".format(
                cur_stack.stack_status) + bcolors.ENDC)

        else:
            idx = 0
            while cur_stack.stack_status != "CREATE_FAILED" and cur_stack.stack_status != "CREATE_COMPLETE":
                cur_stack = get_stack(HEAT, STK_NAME)
                print(bcolors.HEADER + "[STACK STATUS]==>" + bcolors.WARNING + "{} [".format(
                      cur_stack.stack_status) + SPINNER[idx] + "]" + bcolors.ENDC, end="\r")
                stdout.flush()
                idx = (idx + 1) % len(SPINNER)
                sleep(1)
            print(bcolors.HEADER + "[STACK STATUS]==>" + bcolors.WARNING + "{} [".format(
                cur_stack.stack_status) + "#]" + bcolors.ENDC)


if __name__ == '__main__':
    main()
