from pathlib import Path

import click


class AFLCollector(object):

    def __init__(self, results):
        self._collector_name = "afl-collector"
        self._results = results

    @property
    def name(self):
        return self._collector_name

    def parse_directory(self, directory):
        click.echo("Reading {}...".format(directory))

        self._parse_afl_command(directory)
        click.echo("afl-fuzz command: {}".format(self._results.command))

        new = self._read_directory(directory)
        old = set([i[1] for i in self._results.all_crashes])

        diff = new - old
        if len(diff) != 0:
            click.echo("Adding {} crashes.".format(len(diff)))

        self._results.save_crashes(diff)

    def gather_all_samples(self, directory):
        samples = set()

        click.echo("Reading {}...".format(directory))
        p = Path(directory)
        for fuzzer_dir in p.iterdir():
            queue_dir = fuzzer_dir / "queue"

            if not queue_dir.exists():
                click.echo("Skipping fuzzer {}...".format(fuzzer_dir.name))
                continue
            else:
                click.echo("Parsing fuzzer {}...".format(fuzzer_dir.name))

            for sample in queue_dir.iterdir():
                if sample.name == "README.txt":
                    continue
                if sample.is_dir():
                    continue
                samples.add(str(sample))

        return samples

    def _parse_afl_command(self, directory):
        p = Path(directory)
        for fuzzer_dir in p.iterdir():
            stats_file = fuzzer_dir / "fuzzer_stats"
            try:
                with stats_file.open() as f:
                    self._results.command = self._parse_fuzzer_stats(f)
                return
            except FileNotFoundError:
                continue

    def _parse_fuzzer_stats(self, stats_file):
        """ Get the command used in afl-fuzz from the fuzzer_stats file.
        """
        for line in stats_file:
            if line.startswith("command_line"):
                command = line.split(":", maxsplit=1)[1].rstrip().lstrip()
                command = command.split("--", maxsplit=1)[1].rstrip().lstrip()
        return command

    def _read_directory(self, directory):
        crashes = set()

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
                        crashes.add(str(c))
                    continue
                crashes.add(str(crash))

        return crashes
