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

    def test_chain_with_dangerous_part_is_blocked(self):
        self.assertFalse(
            check_command("echo hello & del /q *.*")[0]
        )

    def test_read_only_chain_is_allowed(self):
        self.assertTrue(check_command("ipconfig & tasklist")[0])

    def test_pipe_to_findstr_is_allowed(self):
        self.assertTrue(
            check_command('ipconfig | findstr /i "ipv4"')[0]
        )

    def test_redirect_to_file_is_blocked(self):
        self.assertFalse(check_command("dir > list.txt")[0])

    def test_common_read_only_commands_are_allowed(self):
        for command in [
            "ipconfig /all",
            "dir *.txt",
            "dir /o:-s",
            'findstr "error" log.txt',
        ]:
            self.assertTrue(check_command(command)[0], command)

    def test_network_command_requires_approval(self):
        is_allowed, message = check_command("ping google.com")
        self.assertTrue(is_allowed)
        self.assertIn("approval", message)

    def test_multiple_lines_are_blocked(self):
        self.assertFalse(
            check_command("ipconfig\ntasklist")[0]
        )


if __name__ == "__main__":
    unittest.main()