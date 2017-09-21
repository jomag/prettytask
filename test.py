
import pytest

from prettytask import prompt, ValidationError, Separator


class fake_input:
    """Fake the builting input function

    The __init__ function takes a number of strings as
    input data. For each call to input() the next string
    is returned.

    If it runs out of data an EOFError is raised.

    If used in a 'with' context and end of the data
    is not reached when finished a RuntimeError is raised.

    Note that pdb does not play well with this!
    """
    
    def __init__(self, *args):
        self.lines = list(args)

    def eoi(self):
        return len(self.lines) == 0

    def _fake_input(self):
        try:
            return self.lines.pop(0)
        except IndexError:
            raise EOFError()

    def __enter__(self):
        self.original = __builtins__["input"]
        __builtins__["input"] = self._fake_input
        return self

    def __exit__(self, exc_type, exc_value, tb):
        __builtins__["input"] = self.original
        if exc_type is None:
            if not self.eoi():
                raise RuntimeError("End of input not reached")
    

def test_fake_input():
    with fake_input("hello", "there"):
        assert input() == "hello"
        assert input() == "there"
        with pytest.raises(EOFError):
            input()

    with pytest.raises(RuntimeError):
        with fake_input("1", "2", "3"):
            input()
            input()


def test_prompt_for_string():
    with fake_input("foo"): 
        assert prompt("enter name", type=str) == "foo"


def test_prompt_for_bool():
    test = lambda: prompt("bool test", type=bool)
    with fake_input("yes", "y", "no", "n"):
        assert test() is True
        assert test() is True
        assert test() is False
        assert test() is False


def test_prompt_for_integer():
    with fake_input("0", "0x0000", "123", "0xBEEF"):
        assert prompt("", type=int) == 0
        assert prompt("", type=int) == 0
        assert prompt("", type=int) == 123
        assert prompt("", type=int) == 0xBEEF


def test_prompt_for_choice():
    choices = ["red", "green", "blue"]
    with fake_input("1", "3", "2"):
        assert prompt("", choices=choices) == "red"
        assert prompt("", choices=choices) == "blue"
        assert prompt("", choices=choices) == "green"


def test_prompt_with_default_value():
    with fake_input("", "", "") as f:
        assert prompt("", type=str, default="foo") == "foo"
        assert prompt("", type=int, default=19) == 19
        assert prompt("", type=bool, default=True) is True
        assert f.eoi()


def test_prompt_validate_string_not_empty():
    with fake_input(""):
        with pytest.raises(EOFError):
            prompt("", empty=False)

    with fake_input(""):
        assert prompt("", empty=True) == ""


def test_prompt_validate_string_max_length():
    with fake_input("123", "12345"):
        prompt("", maxlen=3, retries=False)
        with pytest.raises(ValidationError):
            prompt("", maxlen=3, retries=False)


def test_integer_prompt_with_empty_input():
    with fake_input("", ""):
        with pytest.raises(ValidationError):
            prompt("empty int", type=int, empty=False, retries=False)

        assert prompt("empty int", type=int, empty=True, retries=False) is None 


def test_prompt_validate_integer_range():
    test = lambda: prompt("validate integer range", type=int, retries=False, min=4, max=6)

    with fake_input("3", "4", "5", "6", "7"):
        with pytest.raises(ValidationError):
            test()

        assert test() == 4
        assert test() == 5
        assert test() == 6

        with pytest.raises(ValidationError):
            test()


def test_choice_prompt_with_separator():
    choices = ["foo", "bar", Separator(), "quit"]
    test = lambda: prompt("", choices=choices, retries=False)
    with fake_input("1", "2", "3", "4"):
        assert test() == "foo"
        assert test() == "bar"
        assert test() == "quit"
        with pytest.raises(ValidationError):
            test()

