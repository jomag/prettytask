
__version__ = "0.0.0"

try:
    import colorama
    RED = colorama.Fore.RED
    GREEN = colorama.Fore.GREEN
    YELLOW = colorama.Fore.YELLOW
    BLUE = colorama.Fore.BLUE
    WHITE = colorama.Fore.WHITE
    RESET = colorama.Style.RESET_ALL
    BRIGHT = colorama.Style.BRIGHT
except:
    RED = ""
    GREEN = ""
    YELLOW = ""
    BLUE = ""
    WHITE = ""
    RESET = ""
    BRIGHT = ""

ERROR_COLOR = BRIGHT + RED
SUCCESS_COLOR = BRIGHT + GREEN
WARNING_COLOR = BRIGHT + YELLOW

WARNING_PREFIX = ""
WARNING_PREFIX_COLOR = WARNING_COLOR
WARNING_MESSAGE_COLOR = WARNING_COLOR

ERROR_PREFIX = ""
ERROR_PREFIX_COLOR = ERROR_COLOR
ERROR_MESSAGE_COLOR = ERROR_COLOR

FATAL_PREFIX = "Fatal error: "
FATAL_PREFIX_COLOR = ERROR_COLOR
FATAL_MESSAGE_COLOR = ERROR_COLOR

TASK_BULLET = " * "
TASK_BULLET_COLOR = BRIGHT + YELLOW
TASK_COLOR = ""

GROUP_LINE_COLOR = BRIGHT + GREEN
GROUP_TEXT_COLOR = BRIGHT + WHITE

# This string is appended to tasks while they are being performed
WORK_IN_PROGRESS = "... "


class Error(Exception):
    def __str__(self):
        return "failed"


def error(msg):
    sys.stderr.write("%s%s%s%s%s\n" % (ERROR_PREFIX_COLOR, ERROR_PREFIX, ERROR_MESSAGE_COLOR, msg, RESET))


def warning(msg):
    sys.stderr.write("%s%s%s%s%s\n" % (WARNING_PREFIX_COLOR, WARNING_PREFIX, WARNING_MESSAGE_COLOR, msg, RESET))


def fatal_error(msg, exit=True):
    """Print an error message to stderr and optionally exit"""
    sys.stderr.write("%s%s%s%s%s\n" % (FATAL_PREFIX_COLOR, FATAL_PREFIX, FATAL_MESSAGE_COLOR, msg, RESET))
    if exit:
        sys.exit(1)


class TaskGroup:
    line_char = "-"

    def __init__(self, description):
        self.description = description
    
    def __enter__(self):
        print("\n%s%s%s" % (GROUP_TEXT_COLOR, self.description, RESET))
        print(GROUP_LINE_COLOR + (TaskGroup.line_char * len(self.description)) + RESET)
        return self

    def __exit__(self, exc_type, exc_value, tb):
        pass


class Task:
    BULLET = TASK_BULLET_COLOR + TASK_BULLET + RESET
    wip = WORK_IN_PROGRESS

    def __init__(self, description):
        self.description = description
        self.finished = False

    def __enter__(self):
        print("%s%s%s%s%s" % (Task.BULLET, TASK_COLOR, self.description, self.wip, RESET), flush=True, end="")
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if not self.finished:
            if exc_type is None:
                self.ok()
            elif exc_type is Error:
                self.error(str(exc_value))
                return True
            else:
                self.error(str(exc_value))

    def ok(self, message="OK"):
        print(("\b" * len(self.wip)) + ": " + SUCCESS_COLOR + message + RESET)
        self.finished = True

    def error(self, message="failed"):
        print(("\b" * len(self.wip)) + ": " + ERROR_COLOR + message + RESET)
        self.finished = True

    def fatal_error(self, message="failed"):
        self.error(message)
        self.finished = True
        sys.exit(1)


def prompt(msg):
    """Prompt for input from the user"""
    print(msg)
    response = input()
    if response not in ["y", "Y"]:
        raise Cancel()
