from atriage.db import (
    AtriageDB, copy_crashes, get_crash_statistics, init_conn
)

from atriage.collectors import afl

from atriage import exploitable as ex

from atriage import asan as _asan

import click

import tabulate


DB_FILE_NAME = "atriage.db"


@click.group(help="A dumb afl-fuzz triage tool.")
@click.pass_context
def cli(ctx):
    ctx.obj = init_conn(DB_FILE_NAME)


@cli.command(help="Triage crash files from afl output directory.")
@click.argument("dir", type=click.Path(exists=True))
@click.pass_obj
def triage(conn, dir):
    r = AtriageDB(conn)
    collector = afl.AFLCollector(r)
    collector.parse_directory(dir)


@cli.command(help="Print information about the provided database file.")
@click.argument("db", type=click.Path(exists=True))
@click.pass_obj
def info(conn, db):
    r = AtriageDB(conn)
    out, total_crashes = get_crash_statistics(r)

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
@click.pass_obj
def list(conn, db, all, index):
    r = AtriageDB(conn)

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
@click.pass_obj
def gather(conn, db, dir, all, index):
    r = AtriageDB(conn)

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
@click.pass_obj
def exploitable(conn, db, out, all, index, timeout, location, abort):
    """ Capture GDB exploitable output of latest triaged crash files.

    This command reuses the parameters passed to your fuzzed app in your
    afl-fuzz run and expects the standard "@@" to denote the place where
    the crash file in inserted into your parameters. The command will fail if
    it does not find that.
    """
    r = AtriageDB(conn)

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
@click.pass_obj
def asan(conn, db, out, all, index, timeout):
    """ Capture ASAN exploitable output of latest triaged crash files.

    This command reuses the parameters passed to your fuzzed app in your
    afl-fuzz run and expects the standard "@@" to denote the place where
    the crash file in inserted into your parameters. The command will fail if
    it does not find that.
    """
    r = AtriageDB(conn)

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
