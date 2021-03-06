from atriage.db import (
    AtriageDB, copy_crashes, get_crash_statistics
)

from atriage.collectors import collectors_index

from atriage.collectors.exceptions import NoopException

from atriage import exploitable as ex

from atriage import asan as _asan

import click

import tabulate


DB_FILE_NAME = "atriage.db"


@click.group(help="A dumb afl-fuzz triage tool.")
def cli():
    pass


@cli.command(help="List supported collectors.")
def list_collectors():
    for key in collectors_index.keys():
        if key == "afl-collector":
            click.echo("{} (default)".format(key))
        else:
            click.echo(key)


@cli.command(help="Triage crash files from afl output directory.")
@click.argument("dir", type=click.Path(exists=True))
@click.option("-c", "--collector", default="afl-collector")
@click.option("--command")
def triage(dir, collector, command):
    try:
        collector = collectors_index[collector]
    except KeyError:
        click.echo("Error: Collector {} invalid. "
                   "Check \"atriage list-collectors\" for a list of "
                   "valid collectors.".format(collector))
        return

    r = AtriageDB(DB_FILE_NAME)

    collector = collector(r)
    r.set_collector(collector.name)
    collector.parse_directory(dir)

    if command:
        r.command = command


@cli.command(help="Print information about the provided database file.")
@click.argument("db", type=click.Path(exists=True))
def info(db):
    r = AtriageDB(db)
    out, total_crashes = get_crash_statistics(r)

    click.echo("Collector: {}".format(r.get_collector()))
    click.echo("Command: {}".format(r.command))
    click.echo()
    click.echo(tabulate.tabulate(out, headers=("index", "crashes")))
    click.echo()
    click.echo("Total crashes: {}".format(total_crashes))


@cli.command(help="List latest triaged crash files.")
@click.argument("db", type=click.Path(exists=True))
@click.option("--all", is_flag=True, default=False,
              help="List all triaged crash files.")
@click.option("--index", type=int, default=-1,
              help="List files at index. "
              "Use atriage info to get a list of indexes.")
def list(db, all, index):
    r = AtriageDB(db)

    if all:
        crashes = [i[1] for i in r.all_crashes]
    else:
        try:
            crashes = [i[1] for i in r.get_result_set(index)]
        except IndexError as e:
            click.echo(str(e))
            return

    for i in crashes:
        click.echo(i)


@cli.command(help="Gather latest triaged crash files.")
@click.argument("db", type=click.Path(exists=True))
@click.argument("dir", type=click.Path())
@click.option("--all", is_flag=True, default=False,
              help="Gather all triaged crash files.")
@click.option("--index", type=int, default=-1,
              help="Gather files at index. "
              "Use atriage info to get a list of indexes.")
def gather(db, dir, all, index):
    r = AtriageDB(db)

    if all:
        crashes = [i[1] for i in r.all_crashes]
    else:
        try:
            crashes = [i[1] for i in r.get_result_set(index)]
        except IndexError as e:
            click.echo(str(e))
            return

    copy_crashes(crashes, dir)


@cli.command()
@click.argument("db", type=click.Path(exists=True))
@click.argument("out", type=click.Path())
@click.option("--all", is_flag=True, default=False,
              help="Capture exploitable output of all triaged crash files.")
@click.option("--index", type=int, default=-1,
              help="Capture exploitable output of files at index. "
              "Use atriage info to get a list of indexes.")
@click.option("--timeout", type=int, default=30,
              help="Duration to spend on a single crash case.")
@click.option("--location", type=click.Path(exists=True),
              envvar="ATRIAGE_EXPLOITABLE",
              help="Location of the exploitable.py script")
@click.option("--abort-on-error", "abort", default=False, is_flag=True,
              help="Set ASAN_OPTIONS=abort_on_error=1")
def exploitable(db, out, all, index, timeout, location, abort):
    """ Capture GDB exploitable output of latest triaged crash files.

    This command reuses the parameters passed to your fuzzed app in your
    afl-fuzz run. The command uses the standard "@@" to denote the place where
    the crash file in inserted into your parameters. If no "@@" is given, the
    crash file will be fed to the command through stdin. """

    if location is None:
        click.echo("Please supply the location of the exploitable.py script. "
                   "You can do this by either setting the ATRIAGE_EXPLOITABLE "
                   "environment variable or using the --location option.")
        return

    r = AtriageDB(db)

    if r.command is None:
        click.echo("No command is set. Please run `atriage triage` again, "
                   "with the --command option if neccessary.")
        return

    if all:
        crashes = r.all_crashes
    else:
        try:
            crashes = r.get_result_set(index)
        except IndexError as e:
            click.echo(str(e))
            return

    try:
        ret = ex.feed_crashes(
            r._conn, r.command, crashes, timeout, location, abort)
    except IndexError as e:
        click.echo(str(e))
        return

    with open(out, "w") as f:
        for i in ret:
            f.write("{}\n".format(i))


@cli.command()
@click.argument("db", type=click.Path(exists=True))
@click.argument("out", type=click.Path())
@click.option("--all", is_flag=True, default=False,
              help="Capture ASAN output of all triaged crash files.")
@click.option("--index", type=int, default=-1,
              help="Capture ASAN output of files at index. "
              "Use atriage info to get a list of indexes.")
@click.option("--timeout", type=int, default=30,
              help="Duration to spend on a single crash case.")
def asan(db, out, all, index, timeout):
    """ Capture ASAN exploitable output of latest triaged crash files.

    This command reuses the parameters passed to your fuzzed app in your
    afl-fuzz run. The command uses the standard "@@" to denote the place where
    the crash file in inserted into your parameters. If no "@@" is given, the
    crash file will be fed to the command through stdin. """
    r = AtriageDB(db)

    if r.command is None:
        click.echo("No command is set. Please run `atriage triage` again, "
                   "with the --command option if neccessary.")
        return

    if all:
        crashes = r.all_crashes
    else:
        try:
            crashes = r.get_result_set(index)
        except IndexError as e:
            click.echo(str(e))
            return

    try:
        ret = _asan.feed_crashes(r._conn, r.command, crashes, timeout)
    except IndexError as e:
        click.echo(str(e))
        return

    with open(out, "w") as f:
        for i in ret:
            f.write("{}\n".format(i))


@cli.command(help="Gather all generated samples.")
@click.argument("dir", type=click.Path(exists=True))
@click.argument("out", type=click.Path())
@click.option("-c", "--collector", default="afl-collector")
def gather_samples(dir, out, collector):
    try:
        collector = collectors_index[collector]
    except KeyError:
        click.echo("Error: Collector {} invalid. "
                   "Check \"atriage list-collectors\" for a list of "
                   "valid collectors.".format(collector))
        return

    collector = collector(None)

    try:
        samples = collector.gather_all_samples(dir)
        click.echo("Found {} samples.".format(len(samples)))
        copy_crashes(samples, out)
    except NoopException:
        click.echo("Command not implemented for selected collector.")
