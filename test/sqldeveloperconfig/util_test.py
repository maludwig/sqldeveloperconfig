import unittest
import xml.etree.ElementTree as ET

from sqldeveloperconfig.preferences import find_pref_path
from sqldeveloperconfig.util import indent_xml, to_pretty_xml, find_all_connection_paths, find_connections_path, ask_default, ask_yes_no

EXPECTED_XML = """<Parent a="b">
  <Child is_baby="true" />
</Parent>
"""


class TestUtils(unittest.TestCase):
    def test_to_pretty_xml(self):
        elem = ET.Element("Parent", attrib={"a": "b"})
        elem_child = ET.Element("Child", attrib={"is_baby": "true"})
        elem.append(elem_child)
        xml_string = to_pretty_xml(elem)
        self.assertEqual(xml_string, EXPECTED_XML)

    def test_file_finding(self):
        all_conns_paths = find_all_connection_paths()
        self.assertEqual(1, len(all_conns_paths))
        initial_conns_path = all_conns_paths[0]
        prefs_path = find_pref_path(initial_conns_path)
        final_conns_path = find_connections_path(prefs_path)
        self.assertEqual(initial_conns_path, final_conns_path)

    def test_ask_default(self):
        user_input = ask_default("Test", default="Never", input_fn=lambda prompt: "")
        self.assertEqual(user_input, "Never")
        user_input = ask_default("Test", default="Never", input_fn=lambda prompt: "Always")
        self.assertEqual(user_input, "Always")
        user_input = ask_default("Test", default="", input_fn=lambda prompt: "")
        self.assertEqual(user_input, "")

    def test_ask_yes_no(self):
        user_input = ask_yes_no("Test", default="y", input_fn=lambda prompt: "")
        self.assertEqual(user_input, True)
        user_input = ask_yes_no("Test", default="n", input_fn=lambda prompt: "")
        self.assertEqual(user_input, False)
        user_input = ask_yes_no("Test", default="y", input_fn=lambda prompt: "y")
        self.assertEqual(user_input, True)
        user_input = ask_yes_no("Test", default="n", input_fn=lambda prompt: "y")
        self.assertEqual(user_input, True)
        user_input = ask_yes_no("Test", default="y", input_fn=lambda prompt: "n")
        self.assertEqual(user_input, False)
        user_input = ask_yes_no("Test", default="n", input_fn=lambda prompt: "n")
        self.assertEqual(user_input, False)
        user_input = ask_yes_no("Test", default="y", input_fn=lambda prompt: "NO")
        self.assertEqual(user_input, False)
        user_input = ask_yes_no("Test", default="n", input_fn=lambda prompt: "YES")
        self.assertEqual(user_input, True)
        user_input = ask_yes_no("Test", default="y", input_fn=lambda prompt: "no")
        self.assertEqual(user_input, False)
        user_input = ask_yes_no("Test", default="n", input_fn=lambda prompt: "yes")
        self.assertEqual(user_input, True)


if __name__ == "__main__":
    unittest.main()
