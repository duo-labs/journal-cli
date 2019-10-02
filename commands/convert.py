import click

from os import path

from constants import POST_DIRECTORY
from converters import convert_file
from commands.util import get_last_modified
from config import config


@click.command()
@click.argument('filename', required=False)
def convert(filename):
    """Converts a non-Markdown post into a format that's acceptable by Journal.

    It converts Jupyter notebooks to Markdown, extracting images and cleaning
    up output cells.

    It converts Rmd files to HTML, parsing out the body of the post into a
    separate file.
    """
    # Get the file we need to work with, making sure it exists
    if not filename:
        filename = get_last_modified(
            path.join(config.get('journal_path'), POST_DIRECTORY))
    elif not path.isabs(filename):
        filename = path.abspath(
            path.join(config.get('journal_path'), POST_DIRECTORY, filename))

    if not path.exists(filename):
        click.secho('File "{}" not found'.format(filename), fg='red')
        return

    # Markdown is supported by default, so we don't need to convert it
    _, ext = path.splitext(filename.lower())
    if ext == '.md':
        click.secho(
            'Markdown is supported already - no conversion needed', fg='green')
        return

    try:
        converted_filename = convert_file(filename)
        click.secho(
            'Converted post to {}'.format(converted_filename), fg='green')
    except Exception as e:
        click.secho(str(e), fg='red')