import re


SAFE_COMMANDS = {
    "ipconfig",
    "tasklist",
    "hostname",
    "whoami",
    "ver",
    "systeminfo",
}


def check_command(command: str) -> tuple[bool, str]:
    """
    Checks whether the generated CMD command
    belongs to the approved read-only command set.
    """

    command = command.strip()

    if not command:
        return False, "Empty command"

    special_responses = {
        "BLOCKED": "Blocked by the agent",
        "UNSUPPORTED": "Unsupported request",
        "NEED_CLARIFICATION": "More information is needed",
    }

    if command in special_responses:
        return False, special_responses[command]

    # Only one command is permitted.
    if "\n" in command or "\r" in command:
        return False, "Multiple lines are not allowed"

    # Reject command chaining and shell operators.
    if re.search(r"[&|<>^%!`]", command):
        return False, "Shell operators are not allowed"

    first_word = command.split()[0].lower()

    if first_word in SAFE_COMMANDS:
        if command.lower() == first_word:
            return True, "Approved read-only command"

    # Allow listing files and sorting by size.
    if re.fullmatch(
        r'dir(?:\s+"[A-Za-z0-9 _.-]+(?:\\[A-Za-z0-9 _.-]+)*"|'
        r'\s+[A-Za-z0-9_.:\\-]+)?(?:\s+/o-s)?',
        command,
        re.IGNORECASE,
    ):
        return True, "Approved directory listing"

    # Allow viewing directory structure.
    if re.fullmatch(
        r'tree(?:\s+"[A-Za-z0-9 _.-]+(?:\\[A-Za-z0-9 _.-]+)*"|'
        r'\s+[A-Za-z0-9_.:\\-]+)?(?:\s+/f)?',
        command,
        re.IGNORECASE,
    ):
        return True, "Approved directory tree"

    return False, "Command is not in the approved list"