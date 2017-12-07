import subprocess

import click


def feed_crashes(command, crashes, timeout):
    command = command.split()
    file_index = None
    for index, token in enumerate(command):
        if token == "@@":
            file_index = index
            break

    if file_index is None:
        raise IndexError("Unable to locate @@ in command.")

    ret = []
    for c in crashes:
        command[file_index] = str(c)
        command_string = " ".join(command)
        try:
            proc = subprocess.run(command, timeout=timeout,
                                  stderr=subprocess.PIPE,
                                  stdout=subprocess.DEVNULL)
            err_msg = proc.stderr.decode("utf-8", "backslashreplace")
        except subprocess.TimeoutExpired:
            err_msg = "Crash case timed out.\n"

        click.echo(command_string)
        click.echo(err_msg)

        ret.append((command_string, err_msg))

    return ret
