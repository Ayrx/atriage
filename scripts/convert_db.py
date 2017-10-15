from atriage.collect import Results

import click

import pickle


@click.command()
@click.argument("infile", type=click.Path(exists=True))
@click.argument("outfile", type=click.Path())
def cli(infile, outfile):
    click.echo("Converting {} to new format...".format(infile))
    with open(infile, "rb") as f:
        results = pickle.load(f)

    r = Results(results)
    with open(outfile, "wb") as f:
        pickle.dump(r, f, pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__":
    cli()
