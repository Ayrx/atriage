from atriage.collect import Results, copy_crashes, get_crash_statistics

import click

import tabulate


DB_FILE_NAME = "atriage.db"


@click.group(help="A dumb afl-fuzz triage tool.")
def cli():
    pass


@cli.command(help="Triage crash files from afl output directory.")
@click.argument("dir", type=click.Path(exists=True))
def triage(dir):
    r = Results(DB_FILE_NAME)
    r.parse_directory(dir)
    r.write()


@cli.command(help="Print information about the provided database file.")
@click.argument("db", type=click.Path(exists=True))
def info(db):
    r = Results(db)
    out, total_crashes = get_crash_statistics(r)

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
    r = Results(db)

    if all:
        crashes = r.all_crashes
    else:
        try:
            crashes = r.get_result_set(index)
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
    r = Results(db)

    if all:
        crashes = r.all_crashes
    else:
        try:
            crashes = r.get_result_set(index)
        except IndexError as e:
            click.echo(str(e))
            return

    copy_crashes(crashes, dir)
