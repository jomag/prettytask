#!/usr/bin/env python

import sys

from prettytask import Task, TaskGroup, Error, prompt, Separator


def main():
    with Task("Checking python version") as task:
        task.result = "%d.%d.%d" % sys.version_info[:3]

    with Task("A quick task"):
        pass

    with Task("A task with a custom success message") as task:
        task.result = "that went well!"

    with Task("A task that fails") as task:
        raise Error

    with Task("A task that fails with a custom error"):
        raise Error("crash and burn...")

    try:
        with Task("A task that fails with some other exception"):
            x = 1 / 0
    except ZeroDivisionError:
        print("   ... the exception was reraised and caught as expected ...")

    with TaskGroup("This marks the start of a set of tasks"):
        with Task("Here's one"):
            pass
        with Task("Another one that fails"):
            raise Error
        with Task("Finally a third one") as task:
            task.result = "all done!"

    x = prompt("What is your name?", type=str, stripped=True, default="Foo")
    print("Hello, {} ({})".format(x, type(x)))

    y = prompt("What is your age?", type=int, default=42, retries=3)
    print("Got it: {} years ({})".format(y, type(y)))

    z = prompt("What is your favourite color?", choices=["red", "green", "blue", Separator("--- Other options:"), "i hate colors"], default="green")
    print("Color: {} ({})".format(z, type(z)))

    w = prompt("Are we done?", type=bool, default=True)
    print("Done? {} ({})".format(w, type(w)))


if __name__ == "__main__":
    main()
