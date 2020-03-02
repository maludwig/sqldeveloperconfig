#!/usr/bin/env python3
"""
Examples:
  # Show help
  python3 -m sqldeveloperconfig --help
  python3 -m sqldeveloperconfig auto --help
  python3 -m sqldeveloperconfig manual --help
  python3 -m sqldeveloperconfig add_connection --help
  python3 -m sqldeveloperconfig set_passwords --help

  # Automatic file mode, show all connections and passwords on command line
  python3 -m sqldeveloperconfig auto

  # Decrypt a specific v4 password
  python3 -m sqldeveloperconfig manual \\
    --encrypted-password mbAyyEhL9pY= \\
    --db-system-id-value 1d5dbbd1-a91e-4298-9a5d-e13b55030b8f

  # Interactively add a connection
  python3 -m sqldeveloperconfig add_connection --interactive

  # Add a connection from a json config file
  python3 -m sqldeveloperconfig add_connection --json-files interactive_connection.json

  # Set passwords matching regex
  python3 -m sqldeveloperconfig set_passwords \\
    --host-regex '^.*localhost.*$' \\
    --user-regex 'system' \\
    --password 'oracle'
"""


import argparse
import json
import re
from collections import OrderedDict
from getpass import getpass

from sqldeveloperconfig.connections import Connections, Connection
from sqldeveloperconfig.constants import DEFAULT_CONN_ATTRS
from sqldeveloperconfig.cryption import decrypt_v4
from sqldeveloperconfig.util import find_all_connection_paths, ask_yes_no, ask_default
from sqldeveloperconfig.preferences import read_db_system_id, find_pref_path, ProductPreferences

EPILOG = __doc__

# Script version
VERSION = "1.0"


def mod_manual_show(args):
    """
    Decrypt a single password with the db_system_id
    """
    decrypted_password = decrypt_v4(args.encrypted_password, args.db_system_id_value)
    return {"password": decrypted_password}


def mod_set_passwords(args):
    """
    Set passwords matching regexes
    """
    all_names = []
    for connections_path in find_all_connection_paths():
        connections = Connections(connections_path)
        for conn_name, conn in connections.items():
            if re.search(args.name_regex, conn.name):
                if re.search(args.user_regex, conn.user):
                    if re.search(args.host_regex, conn.host):
                        all_names.append(conn.name)
                        conn.plaintext_password = args.password
        connections.save_connections_and_folders(connections_path)
    return all_names


def mod_auto_show(args):
    """
    Show all passwords in all configs
    """
    all_conn_files = OrderedDict()
    for connections_path in find_all_connection_paths():
        connections = Connections(connections_path)
        all_conn_files[connections_path] = OrderedDict()
        all_conn_files[connections_path]["connections"] = connections.to_json()
        all_conn_files[connections_path]["db_system_id"] = connections.prod_prefs.db_system_id
    return all_conn_files


def mod_add_connection(args):
    """
    Add one or more connections
    """

    if args.interactive:
        hostname = ask_default("Enter the hostname of the Oracle SQL server", "localhost")
        port = ask_default("Enter the port", "1521")
        username = ask_default("Enter the username", "system")
        sid = ask_default("Enter the SID", "xe")
        plaintext_password = getpass("Password: ")
        attrs = OrderedDict(
            [
                ("hostname", hostname),
                ("customUrl", "jdbc:oracle:thin:@{}:{}:{}".format(hostname, port, sid)),
                ("sid", sid),
                ("port", port),
                ("user", username),
                ("plaintext_password", plaintext_password),
            ]
        )
        if plaintext_password != "":
            attrs["SavePassword"] = "true"
        else:
            attrs["SavePassword"] = "false"
        for key, default_val in DEFAULT_CONN_ATTRS.items():
            if key not in attrs:
                attrs[key] = ask_default("Value for '{}'".format(key), default_val)
        if ask_yes_no("Save connection config to file for future use with --json-file argument?", default="y"):
            file_path = ask_default("Enter a file path: ", "interactive_connection.json")
            with open(file_path, "w") as conn_file:
                json.dump(attrs, conn_file, indent=2)
        if ask_yes_no("Add connection now?", default="y"):
            for connections_path in find_all_connection_paths():
                pref_path = find_pref_path(connections_path)
                prod_pref = ProductPreferences(pref_path)
                connections = Connections(connections_path)
                connection = Connection(prod_pref.db_system_id, **attrs)
                connections.add_connection(connection)
                connections.save_connections_and_folders(connections_path)
    else:
        if args.json_files:
            for json_path in args.json_files:
                with open(json_path) as json_file:
                    json_str = json_file.read()
                    args.jsons.append(json_str)
        if args.jsons:
            connection_attrs_list = []
            for json_str in args.jsons:
                conn_attrs_or_list = json.loads(json_str)
                if isinstance(conn_attrs_or_list, list):
                    connection_attrs_list += conn_attrs_or_list
                else:
                    connection_attrs_list.append(conn_attrs_or_list)
            all_conn_files = OrderedDict()
            all_connections_paths = find_all_connection_paths()
            if len(all_connections_paths) == 0:
                raise Exception("Connections path not found, please make at lease one connection in SQLDeveloper")
            for connections_path in all_connections_paths:
                pref_path = find_pref_path(connections_path)
                db_system_id = read_db_system_id(pref_path)
                connections = Connections(connections_path)
                for conn_attrs in connection_attrs_list:
                    connection = Connection(db_system_id, **conn_attrs)
                    connections.add_connection(connection)
                all_conn_files[connections_path] = connections.to_json()
                connections.save_connections_and_folders(connections_path)
            return all_conn_files


def parse_args():
    main_parser = argparse.ArgumentParser(
        "sqldeveloperpasswords",
        "python3 -m sqldeveloperpasswords",
        "Work with config of sqldeveloper",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = main_parser.add_subparsers(help="Module", dest="module")

    manual_show_desc = "Decrypt one specific password"
    manual_parser = subparsers.add_parser("manual_show", aliases=["manual"], help=manual_show_desc, description=manual_show_desc)
    manual_parser.add_argument("-p", "--encrypted-password", help="Password that you want to decrypt", required=True)
    manual_parser.add_argument(
        "-d",
        "--db-system-id-value",
        help='machine-unique value of "db.system.id" attribute in the "product-preferences.xml" file, or the export file encryption key.',
        required=True,
    )
    manual_parser.set_defaults(func=mod_manual_show)

    auto_desc = "Automatically list and decrypt all passwords in all connections for all installs of SQLDeveloper"
    auto_parser = subparsers.add_parser("auto_show", aliases=["auto"], help=auto_desc, description=auto_desc)
    auto_parser.set_defaults(func=mod_auto_show)

    set_passwords_desc = "Automatically set all passwords matching the regex"
    set_passwords_parser = subparsers.add_parser("set_passwords", help=set_passwords_desc, description=set_passwords_desc)
    set_passwords_parser.add_argument("--name-regex", default=".*", help="Regex to match the connection name")
    set_passwords_parser.add_argument("--user-regex", default=".*", help="Regex to match the user name")
    set_passwords_parser.add_argument("--host-regex", default=".*", help="Regex to match the host name")
    set_passwords_parser.add_argument("--password", default="", help="New password (if omitted, you will be prompted)")
    set_passwords_parser.set_defaults(func=mod_set_passwords)

    add_connection_desc = "Add connection"
    add_connection_parser = subparsers.add_parser("add_connection", aliases=["add_connections"], help=add_connection_desc, description=add_connection_desc)
    add_connection_parser.add_argument("--interactive", action="store_true", help="Add interactively")
    add_connection_parser.add_argument("--jsons", default=[], nargs="*", type=str, help="Add connection(s) with JSON")
    add_connection_parser.add_argument("--json-files", nargs="*", type=str, help="Add connection(s) from JSON file(s)")
    add_connection_parser.set_defaults(func=mod_add_connection)

    args = main_parser.parse_args()
    if args.module == "manual":
        args.module = "manual_show"
    elif args.module == "auto":
        args.module = "auto_show"
    elif args.module == "set_passwords":
        if args.password == "":
            args.password = getpass("New password")
    return args


def main():
    args = parse_args()
    result = args.func(args)
    print(json.dumps({"result": result, "status": "ok"}, indent=2))


if __name__ == "__main__":
    main()
