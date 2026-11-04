import unittest

from prompt_engineering_poject.safety import check_command


class TestCommandSafety(unittest.TestCase):

    def test_ipconfig_is_allowed(self):
        self.assertTrue(check_command("ipconfig")[0])

    def test_tasklist_is_allowed(self):
        self.assertTrue(check_command("tasklist")[0])

    def test_dir_is_allowed(self):
        self.assertTrue(check_command("dir")[0])

    def test_tree_is_allowed(self):
        self.assertTrue(check_command("tree")[0])

    def test_delete_is_blocked(self):
        self.assertFalse(check_command("del *")[0])

    def test_shutdown_is_blocked(self):
        self.assertFalse(check_command("shutdown /s")[0])

    def test_format_is_blocked(self):
        self.assertFalse(check_command("format C:")[0])

    def test_unknown_command_is_blocked(self):
        self.assertFalse(check_command("unknowncommand")[0])

    def test_command_chaining_is_blocked(self):
        self.assertFalse(
            check_command("ipconfig & tasklist")[0]
        )

    def test_multiple_lines_are_blocked(self):
        self.assertFalse(
            check_command("ipconfig\ntasklist")[0]
        )


if __name__ == "__main__":
    unittest.main()