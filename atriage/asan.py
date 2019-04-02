import re

import subprocess

import click


ASAN_REGEX = re.compile(
    "={65}\n(.*)\n==[0-9]*==ABORTING",
    flags=re.DOTALL
)


def feed_crashes(conn, command, crashes, timeout):
    command = command.split()
    file_index = None
    for index, token in enumerate(command):
        if token == "@@":
            file_index = index
            break

    ret = []
    for crash_id, c in crashes:
        if file_index:
            command[file_index] = str(c)
            command_string = " ".join(command)
            inp = None
        else:
            command_string = " ".join(command)
            with open(c, "rb") as f:
                inp = f.read()

        try:
            proc = subprocess.run(command, timeout=timeout,
                                  input=inp,
                                  stderr=subprocess.STDOUT,
                                  stdout=subprocess.PIPE)
            asan_msg = proc.stdout.decode("utf-8", "backslashreplace")
            asan_output = ASAN_REGEX.search(asan_msg)
        except subprocess.TimeoutExpired:
            out_msg = "---CRASH SUMMARY---\n"
            out_msg += "Filename: {}\n".format(str(c))
            out_msg += "Command: {}\n".format(command_string)
            out_msg += "Crash case timed out.\n"
            out_msg += "---END SUMMARY---"

            click.echo(out_msg)
            ret.append(out_msg)
            continue

        if asan_output:
            asan_output = asan_output.group(1)

            save_crashes(conn, crash_id, asan_output)

            out_msg = "---CRASH SUMMARY---\n"
            out_msg += "Filename: {}\n".format(str(c))
            out_msg += "Command: {}\n".format(command_string)
            out_msg += "{}\n".format(asan_output)
            out_msg += "---END SUMMARY---"

            click.echo(out_msg)
            ret.append(out_msg)

    return ret


def save_crashes(conn, crash_id, asan_output):
    conn.execute("""INSERT OR IGNORE INTO asan (
                      crash_id,
                      asan_output
                    ) VALUES (?, ?)""", (int(crash_id), asan_output, ))
    conn.commit()
