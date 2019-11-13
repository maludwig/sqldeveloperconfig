import unittest

from sqldeveloperconfig.preferences import ProductPreferences, find_all_pref_paths, find_pref_path, find_db_system_id
from sqldeveloperconfig.util import find_connections_path


class TestPreferences(unittest.TestCase):
    def test_find_paths(self):
        all_pref_paths = find_all_pref_paths()
        self.assertEqual(len(all_pref_paths), 1)
        initial_prefs_path = all_pref_paths[0]
        conns_path = find_connections_path(initial_prefs_path)
        final_prefs_path = find_pref_path(conns_path)
        self.assertEqual(initial_prefs_path, final_prefs_path)

    def test_find_db_system_id(self):
        all_pref_paths = find_all_pref_paths()
        preferences = ProductPreferences(all_pref_paths[0])
        db_system_id = preferences.db_system_id
        self.assertRegexpMatches(db_system_id, r"^[a-f0-9]*-[a-f0-9]*-[a-f0-9]*-[a-f0-9]*-[a-f0-9]*$")


if __name__ == "__main__":
    unittest.main()
