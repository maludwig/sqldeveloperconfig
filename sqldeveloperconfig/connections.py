#!/usr/bin/env python
"""
Represents the connections.xml file
"""
import xml.etree.ElementTree as ET
from collections import OrderedDict, defaultdict
from typing import ItemsView

from sqldeveloperconfig.constants import XML_DOCTYPE, DEFAULT_CONN_ATTRS
from sqldeveloperconfig.cryption import decrypt_v4, encrypt_v4
from sqldeveloperconfig.preferences import find_pref_path, ProductPreferences
from sqldeveloperconfig.util import to_pretty_xml


def make_attr_xml(attr_name, attr_val):
    """
    Template XML for a single attribute of a connection
    """
    attr_elem = ET.Element("StringRefAddr", attrib={"addrType": attr_name})
    content_elem = ET.Element("Contents")
    if attr_val is not None:
        if isinstance(attr_val, str):
            content_elem.text = attr_val
        elif isinstance(attr_val, (bytes, bytearray)):
            content_elem.text = attr_val.decode("utf8")
        else:
            raise Exception("Unsure how to serialize {} value to string: '{}'".format(attr_name, attr_val))
    attr_elem.append(content_elem)
    return attr_elem


def make_conn_xml(attrs):
    """
    Template XML for a connection
    """
    ref_elem = ET.Element("Reference", attrib={"name": attrs["ConnName"], "className": "oracle.jdeveloper.db.adapter.DatabaseProvider", "xmlns": ""})
    ref_elem.append(ET.Element("Factory", attrib={"className": "oracle.jdevimpl.db.adapter.DatabaseProviderFactory1212"}))
    ref_addrs_elem = ET.Element("RefAddresses")
    for attr_key, attr_val in attrs.items():
        if attr_key != "password" or attrs["SavePassword"] == "true":
            attr_elem = make_attr_xml(attr_key, attr_val)
            ref_addrs_elem.append(attr_elem)
    ref_elem.append(ref_addrs_elem)
    return ref_elem


class Connection:
    """
    Represents a single connection in SQLDeveloper
    """

    def __init__(self, db_system_id, **kwattrs):
        self.db_system_id = db_system_id
        self._attrs = OrderedDict()
        self._attrs.update(kwattrs)
        for key in DEFAULT_CONN_ATTRS:
            if key not in self._attrs:
                self._attrs[key] = DEFAULT_CONN_ATTRS[key]
        if "plaintext_password" in self._attrs:
            plaintext_password = self._attrs.pop("plaintext_password")
            self.plaintext_password = plaintext_password
        if "folder" in self._attrs:
            self.folder = self._attrs.pop("folder")
        else:
            self.folder = ""

    @property
    def name(self):
        return self._attrs["ConnName"]

    @name.setter
    def name(self, new_value):
        self._attrs["ConnName"] = new_value

    @property
    def user(self):
        return self._attrs["user"]

    @user.setter
    def user(self, new_value):
        self._attrs["user"] = new_value

    @property
    def encrypted_password(self):
        return self._attrs.get("password", None)

    @encrypted_password.setter
    def encrypted_password(self, new_value):
        if isinstance(new_value, (bytes, bytearray)):
            self._attrs["password"] = new_value.decode("utf8")
        else:
            self._attrs["password"] = new_value
        self._attrs["SavePassword"] = "true"

    @property
    def plaintext_password(self):
        if self.encrypted_password is None:
            return None
        return decrypt_v4(self.encrypted_password, self.db_system_id)

    @plaintext_password.setter
    def plaintext_password(self, new_password):
        self.encrypted_password = encrypt_v4(new_password, self.db_system_id)

    @property
    def host(self):
        return self._attrs["customUrl"]

    @host.setter
    def host(self, new_value):
        self._attrs["customUrl"] = new_value

    def to_json(self):
        json_dict = OrderedDict()
        json_dict["folder"] = self.folder
        json_dict["plaintext_password"] = self.plaintext_password
        json_dict.update(self._attrs)
        return json_dict

    def to_xml_elem(self):
        return make_conn_xml(self._attrs)

    def to_xml(self):
        return to_pretty_xml(self.to_xml_elem())

    @classmethod
    def from_xml(cls, db_system_id, xml_ref_entry):
        conn_info = OrderedDict()
        for ref_address_entry in xml_ref_entry.findall("./RefAddresses/StringRefAddr"):
            key = ref_address_entry.attrib["addrType"]
            value_elem = ref_address_entry.find("./Contents")
            value = value_elem.text
            conn_info[key] = value
        return Connection(db_system_id, **conn_info)


class Connections:
    """
    Represents a connections file in SQLDeveloper
    """

    def __init__(self, connections_file_path):
        self.connections = OrderedDict()
        pref_path = find_pref_path(connections_file_path)
        self.prod_prefs = ProductPreferences(pref_path)
        db_system_id = self.prod_prefs.db_system_id

        self.tree = ET.parse(connections_file_path)
        self.root = self.tree.getroot()
        for ref_entry in self.root.findall("./Reference"):
            conn = Connection.from_xml(db_system_id, ref_entry)
            self.add_connection(conn)
        for dir_name, conn_names in self.prod_prefs.load_all_connection_dirs().items():
            for conn_name in conn_names:
                if conn_name in self.connections:
                    self.connections[conn_name].folder = dir_name

    def __iter__(self):
        return self.connections.keys()

    def items(self) -> ItemsView[str, Connection]:
        return self.connections.items()

    def add_connection(self, connection):
        if connection.name in self.connections:
            old_conn = self.connections[connection.name]
            if connection.plaintext_password == "":
                connection.encrypted_password = old_conn.encrypted_password
        self.connections[connection.name] = connection

    def pop_connection(self, connection_name):
        return self.connections.pop(connection_name)

    def to_json(self):
        all_conns_dict = OrderedDict([(conn_name, conn.to_json()) for conn_name, conn in self.connections.items()])
        return all_conns_dict

    def to_xml_elem(self):
        references_elem = ET.Element("References", attrib={"xmlns": "http://xmlns.oracle.com/adf/jndi"})
        for conn_name, conn in self.items():
            references_elem.append(conn.to_xml_elem())
        return references_elem

    def to_xml(self):
        return to_pretty_xml(self.to_xml_elem())

    def to_xml_doc(self):
        return XML_DOCTYPE + to_pretty_xml(self.to_xml_elem())

    def save_folders(self):
        connection_dirs = defaultdict(list)
        for conn_name, conn in self.items():
            if conn.folder:
                connection_dirs[conn.folder].append(conn_name)
        self.prod_prefs.update_all_connection_dirs(connection_dirs)
        self.prod_prefs.save_xml()

    def save_xml(self, connections_path):
        pretty_xml = self.to_xml_doc()
        with open(connections_path, "w") as redone_file:
            redone_file.write(pretty_xml)
        self.save_folders()

    @classmethod
    def from_connections_file_path(cls, connections_file_path):
        return Connections(connections_file_path)
