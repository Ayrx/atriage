from atriage.collectors.exceptions import NoopException
from atriage.collectors.interface import CollectorInterface

from pathlib import Path

import click


class FlatDirCollector(object):

    def __init__(self, results):
        self._collector_name = "flat-dir-collector"
        self._results = results

    @property
    def name(self):
        return self._collector_name

    def parse_directory(self, directory):
        click.echo("Reading {}...".format(directory))

        new = self._read_directory(directory)
        old = set([i[1] for i in self._results.all_crashes])

        diff = new - old
        if len(diff) != 0:
            click.echo("Adding {} crashes.".format(len(diff)))

        self._results.save_crashes(diff)

    def gather_all_samples(self, directory):
        raise NoopException

    def _read_directory(self, directory):
        crashes = set()
        p = Path(directory)
        for crash in p.iterdir():
            crashes.add(str(crash))
        return crashes


CollectorInterface.register(FlatDirCollector)
