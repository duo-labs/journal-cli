import sys

import click

from os import path
from datetime import datetime

from config import config
from commands.author import create_author, generate_author_path
from commands.util import launch_editor, parse_template, generate_post_path


def load_template(filename, daily=False):
    """Loads the correct filepath to the template based on the provided filename.

    If the path to the template is relative, we will assume it's located in the
    templates/ directory. Otherwise, we'll return the absolute path since
    that's what was specified by the user in the configuraiton.

    Arguments:
        filename {str} -- [description]
        daily {bool} -- Whether or not this is a daily post
    """
    template = ''
    if daily:
        template = config['templates'].get('daily_log')

    else:
        _, ext = path.splitext(filename.lower())
        template = config['templates'].get(ext[1:])

    if not path.isabs(template):
        template = path.abspath(
            path.join(path.dirname(__file__), '../templates', template))
    return template


@click.command()
@click.argument('filename', required=False)
@click.option(
    '--template',
    '-t',
    default=None,
    help='The template to use when creating the new post',
    type=click.Path())
def create(filename, template):
    """Creates a new Journal post.

    If no filename is specified, we'll create a daily post. If no template is
    specified, the default template for the provided filetype is used.
    """
    TEMPLATE_CONTEXT = {
        'now': datetime.utcnow,
        'username': config['username'],
    }

    while not path.exists(generate_author_path(config['username'])):
        click.secho(
            'Author {} does not exist. Let\'s create that author now'.format(
                config['username']),
            fg='yellow')
        create_author(config['username'], None, None)

    # Handle the default case of making a new daily post
    daily = False
    if not filename:
        filename = 'daily-log-{}.md'.format(
            datetime.now().strftime('%m-%d-%Y'))
        daily = True

    filepath = generate_post_path(filename)

    # Validate the filename to make sure it has a valid extension
    basename, ext = path.splitext(filename.lower())
    if ext[1:] not in config['templates']:
        click.secho(
            'Unknown extension found for file {}. Valid extensions are {}'.
            format(
                filename, ', '.join(extension
                                    for extension in config['templates']
                                    if extension != 'daily_log')),
            fg='red')
        return

    TEMPLATE_CONTEXT['title'] = basename.replace('_', ' ').replace('-', ' ')

    if not template:
        template = load_template(filename, daily=daily)

    if not path.exists(template):
        click.secho(
            'Error - Template "{}" not found.'.format(template), fg='red')

    output = parse_template(template, TEMPLATE_CONTEXT)
    if path.exists(filepath):
        click.secho(
            'The file at "{}" already exists.'.format(filepath), fg='red')
        return

    # TODO: Make the directory if it doesn't exist

    with open(filepath, 'w') as output_file:
        output_file.write(output)

    click.secho('Post "{}" created.'.format(filepath), fg='green')

    if config['editor'].get('enabled'):
        launch_editor(filepath)
        sys.exit(0)