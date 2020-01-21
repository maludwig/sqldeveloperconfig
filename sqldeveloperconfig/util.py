import glob
from copy import deepcopy
from os.path import join, dirname
from pathlib import Path
from xml.etree import ElementTree as ET


def indent_xml(elem, level=0):
    """
    Indents an Element for pretty printing XML
    """
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent_xml(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def to_pretty_xml(elem: ET.Element) -> str:
    """
    Returns a string of pretty, indented XML, representing an Element
    """
    elem_copy = deepcopy(elem)
    indent_xml(elem_copy)
    byte_string = ET.tostring(elem_copy)
    return byte_string.decode()


def find_all_connection_paths():
    """
    Finds every connections.xml file path
    """
    sql_pref_path = join(str(Path.home()), ".sqldeveloper")
    connections_paths = glob.glob(sql_pref_path + "/system*/o.jdeveloper.db.connection*/connections.xml")
    return connections_paths


def find_connections_path(pref_path):
    """
    Given a preferences.xml path, returns the path to connections.xml
    """
    system_dir = dirname(dirname(pref_path))
    all_connections_paths = glob.glob(system_dir + "/o.jdeveloper.db.connection*/connections.xml")
    if len(all_connections_paths) == 1:
        return all_connections_paths[0]
    else:
        if len(all_connections_paths) == 0:
            raise Exception("No connections files found")
        else:
            raise Exception("Multiple connections files found")


def ask_yes_no(prompt, default="", input_fn=input) -> bool:
    """
    Ask the user for a yes or no response, returns True for yes, False for no
    """
    if default == "":
        user_input = input_fn(prompt + " ").lower()
        if user_input == "":
            return ask_yes_no(prompt, default, input_fn)
    elif default == "y":
        user_input = input_fn(prompt + " [Y/n]: ").lower()
        if user_input == "":
            user_input = "y"
    elif default == "n":
        user_input = input_fn(prompt + " [y/N]: ").lower()
        if user_input == "":
            user_input = "n"
    else:
        raise Exception("Unknown default value for prompt: {}".format(default))
    return user_input[0] == "y"


def ask_default(prompt, default="", input_fn=input) -> str:
    """
    Ask the user for input, with a default
    """
    user_input = input_fn("{} [{}]: ".format(prompt, default))
    if user_input == "":
        user_input = default
    return user_input
