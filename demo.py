from prettytask import Task, TaskGroup, Error


def main():
    with Task("A quick task"):
        pass

    with Task("A task with a custom success message") as task:
        task.ok("that went well!") 

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
            task.ok("all done!")



if __name__ == "__main__":
    main()

