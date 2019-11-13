#!/usr/bin/env python
"""
Represents the product-preferences.xml file
"""
import glob
from collections import OrderedDict
from os.path import dirname, join
from pathlib import Path
from xml.etree import ElementTree as ET

from sqldeveloperconfig.constants import XML_DOCTYPE
from sqldeveloperconfig.util import to_pretty_xml


def make_connection_dir_xml(dir_name, connection_names):
    connection_dir_elem = ET.Element("list", attrib={"n": dir_name})
    for conn_name in connection_names:
        connection_dir_elem.append(ET.Element("string", attrib={"v": conn_name}))
    return connection_dir_elem


def update_all_connection_dirs_xml(prefs_root, connection_dirs):
    ide_conns_elem = prefs_root.find(".//hash[@n='DatabaseFoldersCache']/hash[@n='Folders']/hash[@n='IdeConnections']")
    for new_dir_name, new_connection_names in connection_dirs.items():
        dir_elem = ide_conns_elem.find("./list[@n='{}']".format(new_dir_name))
        if dir_elem is not None:
            ide_conns_elem.remove(dir_elem)
        new_dir_elem = make_connection_dir_xml(new_dir_name, new_connection_names)
        ide_conns_elem.append(new_dir_elem)


def find_pref_path(conn_path):
    system_dir = dirname(dirname(conn_path))
    all_prefs_paths = glob.glob(system_dir + "/o.sqldeveloper.[0-9]*/product-preferences.xml")
    if len(all_prefs_paths) == 1:
        return all_prefs_paths[0]
    else:
        raise Exception("Multiple connections files found")


def find_db_system_id(root):

    elem = root.find(".//value[@n='db.system.id']")
    if isinstance(elem, ET.Element):
        db_system_id_value = elem.get("v", "")
        return db_system_id_value
    else:
        raise Exception("db.system.id not found")


def read_db_system_id(pref_path):
    tree = ET.parse(pref_path)
    root = tree.getroot()
    return find_db_system_id(root)


class ProductPreferences:
    def __init__(self, file_path):
        self.file_path = file_path
        self.tree = ET.parse(self.file_path)
        self.root = self.tree.getroot()

    @property
    def db_system_id(self):
        return find_db_system_id(self.root)

    def update_all_connection_dirs(self, connection_dirs):
        ide_conns_elem = self.root.find(".//hash[@n='DatabaseFoldersCache']/hash[@n='Folders']/hash[@n='IdeConnections']")
        for new_dir_name, new_connection_names in connection_dirs.items():
            dir_elem = ide_conns_elem.find("./list[@n='{}']".format(new_dir_name))
            if dir_elem is not None:
                ide_conns_elem.remove(dir_elem)
            new_dir_elem = make_connection_dir_xml(new_dir_name, new_connection_names)
            ide_conns_elem.append(new_dir_elem)

    def load_all_connection_dirs(self):
        ide_conns_elem = self.root.find(".//hash[@n='DatabaseFoldersCache']/hash[@n='Folders']/hash[@n='IdeConnections']")
        connection_dirs = OrderedDict()
        for dir_elem in ide_conns_elem.findall("./list"):
            connection_names = []
            for conn_name_elem in dir_elem.findall("./string"):
                connection_names.append(conn_name_elem.get("v"))
            connection_dirs[dir_elem.get("n")] = connection_names
        return connection_dirs

    def to_json(self):
        all_conns_dict = OrderedDict([("db_system_id", self.db_system_id), ("connection_dirs", self.load_all_connection_dirs())])
        return all_conns_dict

    def to_xml_elem(self):
        return self.root

    def to_xml(self):
        return to_pretty_xml(self.to_xml_elem())

    def to_xml_doc(self):
        return XML_DOCTYPE + to_pretty_xml(self.to_xml_elem())

    def save_xml(self):
        pretty_xml = self.to_xml_doc()
        with open(self.file_path, "w") as redone_file:
            redone_file.write(pretty_xml)

    @classmethod
    def from_connections_file_path(cls, connections_file_path):
        pref_path = find_pref_path(connections_file_path)
        return ProductPreferences(pref_path)


def find_all_pref_paths():
    sql_pref_path = join(str(Path.home()), ".sqldeveloper")
    prefs_paths = glob.glob(sql_pref_path + "/system*/o.sqldeveloper.[0-9]*/product-preferences.xml")
    return prefs_paths
