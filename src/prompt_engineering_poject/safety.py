import re


READ_ONLY_PATTERNS = [
    r"ipconfig(?:\s+/all)?",
    r"tasklist",
    r"hostname",
    r"whoami",
    r"ver",
    r"winver",
    r"systeminfo",
    r"getmac",
    # dir / tree with an optional path or wildcard, and sort or display flags
    r'dir(?:\s+"[^"]+"|\s+[A-Za-z0-9_.:*?\-]+)?(?:\s+/(?:o:?-?[a-z]+|[bsa]))*',
    r'tree(?:\s+"[^"]+"|\s+[A-Za-z0-9_.:\-]+)?(?:\s+/f)?',
    # findstr [flags] term [file]
    r'findstr(?:\s+/[a-z:]+)*\s+(?:"[^"]*"|[^\s"]+)(?:\s+[A-Za-z0-9_.:*\-]+)?',
]

# Commands that are valid but should get user approval before running:
# network access and administrative tools.
RISKY_PATTERNS = [
    r"ping(?:\s+-[a-z]\s+\d+)?\s+[A-Za-z0-9.-]+",
    r"fsutil\s+volume\s+diskfree\s+[A-Za-z]:",
    r"""wmic\s+logicaldisk(?:\s+where\s+"DeviceID='[A-Za-z]:'")?\s+get\s+[A-Za-z, ]+""",
]


def _matches_any(patterns: list[str], command: str) -> bool:
    return any(
        re.fullmatch(pattern, command, re.IGNORECASE)
        for pattern in patterns
    )


def check_command(command: str) -> tuple[bool, str]:
    """
    Checks a generated CMD command against the approved command set.
    Returns whether it is allowed, and a message explaining why.
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

    # Only one line is permitted.
    if "\n" in command or "\r" in command:
        return False, "Multiple lines are not allowed"

    # Reject redirection, escaping and variable expansion.
    if re.search(r"[<>^%!`]", command):
        return False, "Shell operators are not allowed"

    # Every part of a chained or piped command must be approved on its own.
    parts = [part.strip() for part in re.split(r"&&|\|\||&|\|", command)]

    is_risky = False

    for part in parts:
        if _matches_any(RISKY_PATTERNS, part):
            is_risky = True
        elif not _matches_any(READ_ONLY_PATTERNS, part):
            return False, "Command is not in the approved list"

    if is_risky:
        return True, "Requires user approval before running"

    return True, "Approved read-only command"
