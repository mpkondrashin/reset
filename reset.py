# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Michael Kondrashin mkondrashin@gmail.com
# See LICENSE.txt
#

from __future__ import print_function
import warnings
import csv
import sys
import argparse

import deepsecurity
from deepsecurity.rest import ApiException


def parse_arguments():
    parser = argparse.ArgumentParser(description="Reset computer overrides")
    parser.add_argument("--apikey", help="API Key", required=True)
    parser.add_argument("--hostname", help="Deep Security Manager hostname", required=True)

    subparsers = parser.add_subparsers(dest='command', help='available commands')

    list_parser = subparsers.add_parser('list', help='list computers')
    list_parser.add_argument('--filename', help='output filename', required=True)

    reset_parser = subparsers.add_parser('reset', help='Reset settings')
    reset_parser.add_argument('--filename', help='csv file with list of computers', required=True)
    reset_parser.add_argument('--antimalware', action='store_true', help='reset anti-malware settings')
    reset_parser.add_argument('--settings', action='store_true', help='reset general computer settings')
    reset_parser.add_argument('--all', action='store_true', help='reset anti-malware and computer settings')

    return parser.parse_args()


def list_computers(api_instance):
    expand_options = deepsecurity.Expand()
    expand_options.add(expand_options.none)
    expand = expand_options.list()
    api_response = api_instance.list_computers(api_version='v1', expand=expand, overrides=False)
    return api_response.computers


def list_computers_to_file(api_instance, f):
    writer = csv.writer(f, dialect='excel', quoting=csv.QUOTE_MINIMAL)
    header = [
        'id',
        'host_name',
        'display_name',
        'last_ip_used',
        'agent_version',
        'platform',
        'policy_id',
        'description'
    ]
    writer.writerow(header)
    for c in list_computers(api_instance):
        writer.writerow([
            c.id,
            c.host_name,
            c.display_name,
            c.last_ip_used,
            c.agent_version,
            c.platform,
            c.policy_id,
            c.description]
        )


def reset_anti_malware(api_instance, computer_id):
    print(f"Reset Anti-Malware settings:", end="")
    sys.stdout.flush()

    am_extension = deepsecurity.AntiMalwareComputerExtension()
    am_extension.state = "inherited"
    am_extension.real_time_scan_configuration_id = 0
    am_extension.manual_scan_configuration_id = 0
    am_extension.scheduled_scan_configuration_id = 0

    computer = deepsecurity.Computer()
    computer.anti_malware = am_extension
    api_instance.modify_computer(computer_id, computer, api_version='v1')
    print(" done")


def iterate_computer_ids(filename):
    with open(filename) as f:
        reader = csv.reader(f, dialect='excel', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            if row[0] == 'id':
                continue
            yield row[0]


def list_computer_settings(api_instance, computer_id):
    expand_options = deepsecurity.Expand()
    expand_options.add(expand_options.computer_settings)
    expand = expand_options.list()
    api_response = api_instance.describe_computer(computer_id, api_version='v1', expand=expand, overrides=True)
    try:
        return api_response.to_dict()['computer_settings'].keys()
    except AttributeError:
        return []


def reset_computer_setting(api_instance, computer_id, setting_name):
    try:
        api_instance.reset_computer_setting(computer_id, setting_name, api_version='v1', overrides=False)
    except ApiException as e:
        if e.status != 404:
            raise


def reset_computer_settings(api_instance, computer_id):
    sys.stdout.flush()
    computer_settings_list = list_computer_settings(api_instance, computer_id)
    count = len(computer_settings_list)
    print(f"Reset {count} Computer Settings: ", end="")
    if count == 0:
        print("skip")
        return
    text_length = 0
    for i, s in enumerate(computer_settings_list):
        reset_computer_setting(api_instance, computer_id, s)
        percent = (i + 1) * 100 // count
        sys.stdout.write(u"\u0008" * text_length)
        pstr = str(percent) + "%"
        text_length = len(pstr)
        print(pstr, end="")
        sys.stdout.flush()
    print()


def main():
    args = parse_arguments()

    print(f"Hostname: {args.hostname}", file=sys.stderr)

    if not sys.warnoptions:
        warnings.simplefilter("ignore")

    configuration = deepsecurity.Configuration()
    configuration.host = args.hostname
    configuration.api_key['api-secret-key'] = args.apikey

    api_instance = deepsecurity.ComputersApi(deepsecurity.ApiClient(configuration))

    if args.command == 'list':
        print("List computers", file=sys.stderr)
        if args.filename:
            with open(args.filename, 'w', newline='') as f:
                list_computers_to_file(api_instance, f)
        else:
            list_computers_to_file(api_instance, sys.stdout)
        return

    if args.command == 'reset':
        print("Reset settings", file=sys.stderr)
        for computer_id in iterate_computer_ids(args.filename):
            print(f"Process computer id: {computer_id}")
            if args.antimalware or args.all:
                reset_anti_malware(api_instance, computer_id)
            if args.settings or args.all:
                reset_computer_settings(api_instance, computer_id)
        return


if __name__ == "__main__":
    main()
