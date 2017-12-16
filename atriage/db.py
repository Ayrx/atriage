from pathlib import Path

import pickle

import click

import shutil

import os


class AtriageDB(object):
    def __init__(self, results):
        self._results = results
        self._command = None

    @property
    def command(self):
        return self._command

    @command.setter
    def command(self, value):
        self._command = value

    @property
    def all_crashes(self):
        return set().union(*self._results)

    @property
    def new_crashes(self):
        return self._results[-1]

    @property
    def raw_crashes(self):
        return self._results

    def get_result_set(self, index):
        """ Get crashes by index.

        Passing -1 as the index returns the latest set of crashes.
        """
        invalid_err = IndexError("Index {} is invalid. Use atriage info to "
                                 "view available indexes.".format(index))

        empty_err = IndexError("Database is empty.")

        if index == -1:
            pass
        elif index < 0:
            raise invalid_err

        try:
            return self._results[index]
        except IndexError:
            if index == -1:
                raise empty_err
            else:
                raise invalid_err

    @classmethod
    def from_db(cls, db_file_name):
        p = Path(db_file_name)
        if p.exists():
            with p.open("rb") as f:
                return pickle.load(f)
        else:
            return cls([])


def write_db(db, outfile):
    """ Write database to file.
    """
    with open(outfile, "wb") as f:
        pickle.dump(db, f, pickle.HIGHEST_PROTOCOL)


def get_crash_statistics(db):
    """ Get crash statistics in a printable format.

    This function returns a tuple. The first value in the tuple is a formatted
    list of strings that is shows the new crashes added every time atriage is
    ran. The second value in the tuple is the total number of crashes.
    """
    out = []
    total_crashes = 0

    for index, value in enumerate(db.raw_crashes):
        num_crashes = len(value)
        total_crashes += num_crashes
        if index == 0:
            out.append((index, "{}".format(num_crashes)))
        else:
            out.append((index, "+{}".format(num_crashes)))

    return out, total_crashes


def copy_crashes(crashes, out):
    try:
        os.makedirs(out)
    except OSError as e:
        pass

    click.echo("Copying {} files...".format(len(crashes)))
    for i in crashes:
        try:
            shutil.copy2(str(i), out)
        except FileNotFoundError:
            click.echo("Error copying {}.".format(i))
