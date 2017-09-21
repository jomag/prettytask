
import sys

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

INPUT_COLOR = BRIGHT + WHITE

# This string is appended to tasks while they are being performed
WORK_IN_PROGRESS = "... "


class Error(Exception):
    def __str__(self):
        return "failed"


class InputError(Exception):
    pass


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


def _print_prompt(msg, default=None, end=""):
    if default is not None:
        default_str = "[%s] " % default
    else:
        default_str = ""
    print(msg + " " + default_str, flush=True, end=end)

def _prompt_input():
    print(INPUT_COLOR, flush=True, end="")
    data = input()
    print(RESET, flush=True, end="")
    return data


def _prompt_input_error(short_msg, long_msg):
    print(ERROR_COLOR + short_msg + ": " + RESET + RED + long_msg + RESET)


def _prompt_string(msg, empty=False, stripped=False, maxlen=None, retries=None, default=None):
    while True:
        _print_prompt(msg)
        value = _prompt_input()

        if stripped:
            value = value.strip()

        if not value:
            if default is not None:
                return default
            if empty is True:
                return value
            else:
                _prompt_input_error("Invalid input", "empty string")

        elif maxlen is not None and len(value) > maxlen:
            _prompt_input_error("Invalid input", "max %d characters" % maxlen)

        else:
            return value

        if retries is not None:
            if retries > 0:
                retries -= 1
            else:
                raise InputError("Retry limit reached")


def _prompt_int(msg, empty=False, retries=None, default=None):
    while True:
        if retries == 0:
            raise InputError("Retry limit reached")
        elif retries is not None:
            retries -= 1

        _print_prompt(msg, default=default)
        inp = _prompt_input().strip()

        if not inp:
            if empty is True:
                return None
            if default is not None:
                return default
            _prompt_input_error("Invalid input", "empty string")
            continue

        try:
            if inp.startswith("0x"):
                value = int(inp, 16)
            else:
                value = int(inp)
        except ValueError:
            _prompt_input_error("Invalid input", "%s is not a valid integer" % inp)
            continue

        return value

def _prompt_bool(msg, empty=False, default=None, retries=None):
    if default is True:
        defstr = "yes"
    elif default is False:
        defstr = "no"
    else:
        defstr = None

    while True:
        if retries == 0:
            raise InputError("Retry limit reached")
        elif retries is not None:
            retries -= 1

        _print_prompt(msg, default=defstr)
        inp = _prompt_input().strip().lower()

        if not inp:
            if empty is True:
                return None
            else:
                inp = defstr

        if not inp:
            _prompt_input_error("Invalid input", "empty value")
            continue

        if inp in ["yes", "y"]:
            return True
        if inp in ["no", "n"]:
            return False

        _prompt_input_error("Invalid input", "please enter yes (y) or no (n)")


def _prompt_choice(msg, choices, empty=False, default=None, retries=None):
    while True:
        if retries == 0:
            raise InputError("Retry limit reached")
        elif retries is not None:
            retries -= 1

        n = 1
        for c in choices:
            print("%d. %s" % (n, c))
            n += 1

        _print_prompt(msg, default=default)
        inp = input().strip()

        if not inp:
            if empty is True:
                return None
            if default is not None:
                return default
            else:
                _prompt_input_error("Invalid input", "no selection")
                continue

        try:
            value = int(inp)
        except ValueError:
            _prompt_input_error("Invalid input", "%s is not a valid choice" % inp)
            continue

        try:
            return choices[value-1]
        except IndexError:
            _prompt_input_error("Invalid input", "%s is not a valid choice" % inp)


def prompt(msg, type=str, choices=None, stripped=False, empty=False, maxlen=None, default=None, retries=None):
    """Prompt for input from the user

    Args:
        msg: Message to display to user
        type: Data type to request from user
        choices: List of choices for the user to select among
        stripped: Strip whitespace from string values
        empty: Allow empty response
        maxlen: Max length for string values
        default: Default value to be returned on empty input from user
        retries: Number of retries before giving up
    """
    if choices:
        return _prompt_choice(msg, choices, empty=empty, default=default)
    elif type is str:
        return _prompt_string(msg, empty=empty, stripped=stripped, maxlen=maxlen, default=default)
    elif type is int:
        return _prompt_int(msg, empty=empty, default=default, retries=retries)
    elif type is bool:
        return _prompt_bool(msg, empty=empty, default=default, retries=retries)
    else:
        raise ValueError("Unsupported type: %s" % type.__class__.__name__)
