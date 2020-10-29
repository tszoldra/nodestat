"""Perform tasks against a remote host."""

from .client import RemoteClient
from os import system, environ
import argparse
from dotenv import load_dotenv
from tabulate import tabulate
from getpass import getpass

tabulate.PRESERVE_WHITESPACE = True


def main():

    parser = argparse.ArgumentParser(description='Show usage of computation nodes.\n Warning: resize the terminal window to a large width.')
    parser.add_argument('config_file', type=str, help='configuration file')
    parser.add_argument('-n', '--name', type=str, nargs='+', help='check only nodes given in the command line (discarding those from config file)')
    parser.add_argument('-s', '--short', action='store_true', help='show the basic info only')

    args = parser.parse_args()

    # Load environment variables from config file
    load_dotenv(args.config_file)

    # Read environment variables
    hostname_list = [hostname for hostname in environ.get('REMOTE_HOSTNAME_LIST').split(" ")]
    user = environ.get('REMOTE_USERNAME')
    remote_path = environ.get('REMOTE_PATH')

    try:
        password = getpass(prompt='Password for remote user ' + user + ':\n')
    except Exception as error:
        password = ''
        print('ERROR', error)

    if args.name:
        hostname_list_copy = args.name
    else:
        hostname_list_copy = hostname_list

    tab_to_print = []

    for idx, hostname in enumerate(hostname_list_copy):
        remote = RemoteClient(hostname, user, password, remote_path)
        print(f"Now checking stats for {hostname} ...", flush=True)
        remote.check_stats()
        remote.disconnect()
        tab_to_print.append(remote.get_stats_row(short=args.short))
        system('clear')
        print(tabulate(tab_to_print, tablefmt='fancy_grid', headers=remote.headers_stats(short=args.short),
                       stralign='right', numalign='right', floatfmt="3.0f"), flush=True)
