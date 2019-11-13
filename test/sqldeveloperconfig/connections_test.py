import re
import unittest

from sqldeveloperconfig.connections import Connections, Connection
from sqldeveloperconfig.util import find_all_connection_paths
from test.sqldeveloperconfig.test_constants import DB_SYSTEM_ID

FAKE_PASSWORD = "Ростов-на-Дону"

FAKE_HOSTNAME = "НижнийНовгород.com"

EXPECTED_HOST_ENTRY = """
<StringRefAddr addrType="host">
<Contents>&#1053;&#1080;&#1078;&#1085;&#1080;&#1081;&#1053;&#1086;&#1074;&#1075;&#1086;&#1088;&#1086;&#1076;.com</Contents>
</StringRefAddr>
"""
FAKE_CONN_CONTENT = """
      </StringRefAddr>
      <StringRefAddr addrType="host">
        <Contents>&#1053;&#1080;&#1078;&#1085;&#1080;&#1081;&#1053;&#1086;&#1074;&#1075;&#1086;&#1088;&#1086;&#1076;.com</Contents>
      </StringRefAddr>
      <StringRefAddr addrType="role">"""


class TestConnections(unittest.TestCase):
    def test_loading_adding_and_removing(self):
        for conn_path in find_all_connection_paths():
            connections = Connections.from_connections_file_path(conn_path)
            connection = Connection(DB_SYSTEM_ID, ConnName="test connection name", host=FAKE_HOSTNAME, plaintext_password=FAKE_PASSWORD)
            connections.add_connection(connection)
            connections.save_xml(conn_path)
            with open(conn_path) as conn_file:
                conn_content = conn_file.read()
                clean_content = re.sub(r"\n[\t ]*", "\n", conn_content)
                clean_host_entry = re.sub(r"\n[\t ]*", "\n", EXPECTED_HOST_ENTRY)
                self.assertTrue(clean_host_entry in clean_content)
            connections.pop_connection(connection.name)
            connections.save_xml(conn_path)
            with open(conn_path) as conn_file:
                conn_content = conn_file.read()
                clean_content = re.sub(r"\n[\t ]*", "\n", conn_content)
                clean_host_entry = re.sub(r"\n[\t ]*", "\n", EXPECTED_HOST_ENTRY)
                self.assertTrue(clean_host_entry not in clean_content)


if __name__ == "__main__":
    unittest.main()
