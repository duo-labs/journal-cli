import sys
import os
import hashlib
import io

import click

from os import path
from datetime import datetime

from config import config
from commands.util import launch_editor, parse_template


def load_dataset_template():
    """
    Finds path to the default dataset template.

    Returns:
        str -- Path to default dataset template.
    """
    return path.join(
        path.dirname(__file__), '../templates', 'dataset_template.md')


def check_pandas_installed():
    import pkgutil
    return pkgutil.find_loader("pandas")


def compute_md5(filename):
    try:
        md5 = hashlib.md5()
        with open(filename, "rb") as fh:
            while True:
                bytes = fh.read(io.DEFAULT_BUFFER_SIZE)
                if not bytes:
                    break
                md5.update(bytes)
        return md5.hexdigest()
    except Exception as e:
        return ''


AUTO_PARSE_EXTS = [".csv", ".tsv", ".json", ".xls", ".xlsx", ".parquet"]
AUTO_PARSE_THRESHOLD = 100e6


def auto_parse_schema(location):
    """
    Attempts to automatically parse the file at location (if local) and extract a schema.
    This function will only parse files that have an extension in AUTO_PARSE_EXTS and are
    smaller than AUTO_PARSE_THRESHOLD bytes.

    The function returns a rendered YAML array if the schema was parsed successfully, None
    otherwise.

    TODO: The parsing is done by Pandas (using the various pd.read_* functions), and the schema 
    is just a stringification of DataFrame.dtypes, which has several downsides (e.g. string columns
    have dtype 'object').

    Returns:
        str -- A rendered YAML containing the schema, suitable for inclusion in the template.
    """
    if not path.exists(location):
        return None
    if not check_pandas_installed():
        click.secho("Pandas is not installed, skipping parsing.", fg="yellow")
        return None

    _, ext = path.splitext(location.lower())
    if ext not in AUTO_PARSE_EXTS:
        click.secho(
            "Unrecognized extension {}, skipping parsing.".format(ext),
            fg="yellow")

    size = path.getsize(location)
    if size > AUTO_PARSE_THRESHOLD:
        click.secho("File is large, skipping parsing.")
        return None

    import pandas as pd

    try:
        if ext == ".csv":
            df = pd.read_csv(location, parse_dates=True, nrows=10)
        elif ext == ".tsv":
            df = pd.read_csv(
                location, delimiter='\t', parse_dates=True, nrows=10)
        elif ext == ".json":
            df = pd.read_json(location)
        elif ext == ".parquet":
            df = pd.read_parquet(location)
        elif ext == ".xls" or ext == ".xlsx":
            df = pd.read_excel(location)

        schema = [
            "- {}: {} [No description]".format(field, str(kind))
            for field, kind in df.dtypes.to_dict().items()
        ]

        click.secho(
            "{} fields automatically parsed. Please check schema for accuracy."
            .format(len(schema)))
        return "\n".join(schema)

    except Exception as e:
        print(e)
        click.secho("Pandas could not parse this file, skipping parsing.")
        return None


def generate_dataset_path(name):
    """
    Returns a suitable path for a new dataset.

    Arguments:
        name {str} -- Name of the dataset

    Returns:
        str -- A dataset path in datasets/
    """
    return path.join(config['journal_path'], 'content', 'datasets', name)


@click.command()
@click.argument('location', required=True)
@click.argument('name', required=False)
def dataset(location, name):
    """Add a new dataset to Journal.
    """

    _, basename = path.split(location)
    stem, ext = path.splitext(basename.lower())
    if not name:
        name = stem

    TEMPLATE_CONTEXT = {
        'now': datetime.utcnow,
        'location': location,
        'format': ext[1:],
        'name': name,
        'username': config['username'],
    }

    dataset_path = generate_dataset_path(name)
    dataset_md_path = path.join(dataset_path, '_index.md')

    if path.exists(dataset_md_path):
        click.secho(
            'A dataset already exist in {}.'.format(dataset_path), fg='red')
        return

    template = load_dataset_template()
    if not path.exists(template):
        click.secho(
            'Error - Template "{}" not found.'.format(template), fg='red')
        return

    TEMPLATE_CONTEXT['schema'] = auto_parse_schema(location)
    TEMPLATE_CONTEXT['md5_hash'] = compute_md5(location)

    output = parse_template(template, TEMPLATE_CONTEXT)

    os.makedirs(dataset_path, exist_ok=True)

    with open(dataset_md_path, 'w') as output_file:
        output_file.write(output)

    click.secho(
        'Dataset {} was created with path "{}".'.format(name, dataset_md_path),
        fg='green')

    if config['editor'].get('enabled'):
        launch_editor(dataset_md_path)
        sys.exit(0)