
import sys

__version__ = "0.0.0"

try:
    import colorama
    RED = colorama.Fore.RED
    GREEN = colorama.Fore.GREEN
    YELLOW = colorama.Fore.YELLOW
    BLUE = colorama.Fore.BLUE
    WHITE = colorama.Fore.WHITE
    BLACK = colorama.Fore.BLACK
    RESET = colorama.Style.RESET_ALL
    BRIGHT = colorama.Style.BRIGHT
except ImportError:
    RED = ""
    GREEN = ""
    YELLOW = ""
    BLUE = ""
    WHITE = ""
    BLACK = ""
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
DEFAULTS_COLOR = BRIGHT + BLACK

# This string is appended to tasks while they are being performed
WORK_IN_PROGRESS = "... "


class Error(Exception):
    def __str__(self):
        return "failed"


class InputError(Exception):
    pass


class ValidationError(Exception):
    pass


class Separator:
    def __init__(self, sep="----------------"):
        self.sep = sep
    def __str__(self):
        return self.sep


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
        default_str = " %s[%s]%s " % (DEFAULTS_COLOR, default, RESET)
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

        try:
            if not value:
                if default is not None:
                    return default
                if empty is True:
                    return value
                else:
                    raise ValidationError("empty data")

            if maxlen is not None and len(value) > maxlen:
                raise ValidationError("max %d characters allowed" % maxlen)

            return value
        except ValidationError as e:
            _prompt_input_error("Validation error", str(e))
            if retries is False or retries == 1:
                raise
            elif retries is not None:
                retries -= 1


def _prompt_int(msg, empty, retries, default, min, max):
    while True:
        _print_prompt(msg, default=default)
        inp = _prompt_input().strip()

        try:
            if not inp:
                if empty is True:
                    return None
                elif default is not None:
                    return default
                else:
                    raise ValidationError("empty data")

            try:
                if inp.startswith("0x"):
                    value = int(inp, 16)
                else:
                    value = int(inp)
            except ValueError:
                raise ValidationError("%s is not a valid integer" % inp)

            if min is not None and value < min:
                raise ValidationError("%d is out of range: min %d" % (value, min))
            if max is not None and value > max:
                raise ValidationError("%d is out of range: max %d" % (value, max))

            return value
        except ValidationError as e:
            _prompt_input_error("Validation error", str(e))
            if retries is False or retries == 1:
                raise
            elif retries is not None:
                retries -= 1

def _prompt_bool(msg, empty=False, default=None, retries=None):
    if default is True:
        defstr = "Y/n"
    elif default is False:
        defstr = "y/N"
    else:
        defstr = None

    while True:
        _print_prompt(msg, default=defstr)
        inp = _prompt_input().strip().lower()

        try:
            if not inp:
                if empty is True:
                    return None
                elif default is True:
                    inp = "yes"
                elif default is False:
                    inp = "no"

            if not inp:
                raise ValidationError("empty data")

            if inp in ["yes", "y"]:
                return True
            if inp in ["no", "n"]:
                return False

            raise ValidationError("please enter yes (y) or no (n)")
        except ValidationError as e:
            _prompt_input_error("Validation error", str(e))
            if retries is False or retries == 1:
                raise
            elif retries is not None:
                retries -= 1


def _prompt_choice(msg, choices, empty, default, retries):
    choices_wo_separators = [c for c in choices if type(c) != Separator]
    
    try:
        default_index = choices_wo_separators.index(default)
        default_str = " %s[%d]%s " % (DEFAULTS_COLOR, default_index + 1, RESET)
    except ValueError:
        default_index = None
        default_str = ""

    while True:
        _print_prompt(msg, end="\n")

        n = 1
        for c in choices:
            if type(c) == Separator:
                print(BRIGHT + BLACK + "  " + str(c) + RESET)
            else:
                if c == default:
                    print("  %s%d) %s %s(default)%s" % (BRIGHT + WHITE, n, c, DEFAULTS_COLOR, RESET))
                else:
                    print("  %d) %s" % (n, c))
                n += 1

        print("  Choice:%s" % default_str, end="", flush=True)
        inp = _prompt_input().strip()

        try:
            if not inp:
                if empty is True:
                    return None
                if default is not None:
                    return default
                else:
                    raise ValidationError("empty selection")

            try:
                value = int(inp)
            except ValueError:
                raise ValidationError("%s is not a valid choice" % inp)
            
            if value < 1 or value > len(choices_wo_separators):
                 raise ValidationError("out of range")

            try:
                return choices_wo_separators[value-1]
            except IndexError:
                raise ValidationError("out of range")
        except ValidationError as e:
            _prompt_input_error("Validation error", str(e))
            if retries is False or retries == 1:
                raise
            elif retries is not None:
                retries -= 1


def prompt(msg, type=str, choices=None, stripped=False, empty=False, maxlen=None, default=None, retries=None, min=None, max=None):
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
        min: Min numeric value
        max: Max numeric value
    """
    if choices:
        return _prompt_choice(msg, choices, empty=empty, default=default, retries=retries)
    elif type is str:
        return _prompt_string(msg, empty=empty, stripped=stripped, maxlen=maxlen, default=default, retries=retries)
    elif type is int:
        return _prompt_int(msg, empty=empty, default=default, retries=retries, min=min, max=max)
    elif type is bool:
        return _prompt_bool(msg, empty=empty, default=default, retries=retries)
    else:
        raise ValueError("Unsupported type: %s" % type.__class__.__name__)
