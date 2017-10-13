from pathlib import Path

import pickle

import click

import shutil

import os


class Results(object):
    def __init__(self, results):
        self._results = results

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

    def parse_directory(self, directory):
        new = self._read_directory(directory)
        old = self.all_crashes

        diff = new - old
        if len(diff) != 0:
            click.echo("Adding {} crashes.".format(len(diff)))
            self._results.append(diff)

    def _read_directory(self, directory):
        crashes = set()
        click.echo("Reading {}...".format(directory))

        p = Path(directory)
        for fuzzer_dir in p.iterdir():
            crash_dir = fuzzer_dir / "crashes"

            if not crash_dir.exists():
                click.echo("Skipping fuzzer {}...".format(fuzzer_dir.name))
                continue
            else:
                click.echo("Parsing fuzzer {}...".format(fuzzer_dir.name))

            for crash in crash_dir.iterdir():
                if crash.name == "README.txt":
                    continue
                # The .cwtidy directory is an artifact of Crashwalk's -tidy
                # option. We want to parse the files in there as well.
                if crash.name == ".cwtidy":
                    for c in crash.iterdir():
                        crashes.add(c)
                    continue
                crashes.add(crash)

        return crashes

    @classmethod
    def from_db(cls, db_file_name):
        p = Path(db_file_name)
        if p.exists():
            with p.open("rb") as f:
                results = pickle.load(f)
        else:
            results = []

        return cls(results)


def write_results(results, outfile):
    """ Write results to file.
    """
    with open(outfile, "wb") as f:
        pickle.dump(results._results, f, pickle.HIGHEST_PROTOCOL)


def get_crash_statistics(results):
    """ Get crash statistics in a printable format.

    This function returns a tuple. The first value in the tuple is a formatted
    list of strings that is shows the new crashes added every time atriage is
    ran. The second value in the tuple is the total number of crashes.
    """
    out = []
    total_crashes = 0

    for index, value in enumerate(results.raw_crashes):
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
