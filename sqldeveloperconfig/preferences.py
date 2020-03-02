#!/usr/bin/env python
"""
Represents the product-preferences.xml file
"""
import glob
from collections import OrderedDict
from os.path import dirname, join, isfile
from pathlib import Path
from xml.etree import ElementTree as ET

from sqldeveloperconfig.constants import XML_DOCTYPE
from sqldeveloperconfig.util import to_pretty_xml


def find_ide_connections_elem(prefs_root):
    dfc_elem = prefs_root.find(".//hash[@n='DatabaseFoldersCache']")
    if not dfc_elem:
        dfc_elem = ET.Element("hash", attrib={"n": "DatabaseFoldersCache"})
        prefs_root.append(dfc_elem)
    folders_elem = dfc_elem.find("./hash[@n='Folders']")
    if not folders_elem:
        folders_elem = ET.Element("hash", attrib={"n": "Folders"})
        dfc_elem.append(folders_elem)
    ide_connections_elem = folders_elem.find("./hash[@n='IdeConnections']")
    if not ide_connections_elem:
        ide_connections_elem = ET.Element("hash", attrib={"n": "IdeConnections"})
        folders_elem.append(ide_connections_elem)
    return ide_connections_elem


def make_connection_dir_xml(dir_name, connection_names):
    connection_dir_elem = ET.Element("list", attrib={"n": dir_name})
    for conn_name in connection_names:
        connection_dir_elem.append(ET.Element("string", attrib={"v": conn_name}))
    return connection_dir_elem


def update_all_connection_dirs_xml(prefs_root, connection_dirs):
    ide_conns_elem = find_ide_connections_elem(prefs_root)
    for new_dir_name, new_connection_names in connection_dirs.items():
        dir_elem = ide_conns_elem.find("./list[@n='{}']".format(new_dir_name))
        if dir_elem is not None:
            ide_conns_elem.remove(dir_elem)
        new_dir_elem = make_connection_dir_xml(new_dir_name, new_connection_names)
        ide_conns_elem.append(new_dir_elem)


def find_pref_path(conn_path):
    system_dir = dirname(dirname(conn_path))
    all_prefs_paths = glob.glob(system_dir + "/o.sqldeveloper*/product-preferences.xml")
    if len(all_prefs_paths) == 1:
        return all_prefs_paths[0]
    else:
        if len(all_prefs_paths) == 0:
            raise Exception("No product-preferences files found")
        else:
            raise Exception("Multiple product-preferences files found")


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
        if not isfile(file_path):
            raise Exception("Could not find product preferences file, you must open SQLDeveloper at least once before running this script")
        self.file_path = file_path
        self.tree = ET.parse(self.file_path)
        self.root = self.tree.getroot()

    @property
    def db_system_id(self):
        return find_db_system_id(self.root)

    def update_all_connection_dirs(self, connection_dirs):
        ide_conns_elem = find_ide_connections_elem(self.root)
        for new_dir_name, new_connection_names in connection_dirs.items():
            dir_elem = ide_conns_elem.find("./list[@n='{}']".format(new_dir_name))
            if dir_elem is not None:
                ide_conns_elem.remove(dir_elem)
            new_dir_elem = make_connection_dir_xml(new_dir_name, new_connection_names)
            ide_conns_elem.append(new_dir_elem)

    def load_all_connection_dirs(self):
        ide_conns_elem = find_ide_connections_elem(self.root)
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
    prefs_paths = glob.glob(sql_pref_path + "/system*/o.sqldeveloper*/product-preferences.xml")
    return prefs_paths
