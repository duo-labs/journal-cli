import click
import os
import getpass

from os import path
from shutil import copyfile

from config import config
from commands.util import parse_template


def load_author_template():
    """
    Finds path to the default author template.

    Returns:
        str -- Path to the default author template.
    """
    return path.join(path.dirname(__file__), '../templates', 'author.md')


def generate_author_path(username):
    """Returns a suitable path for a new author.

    Arguments:
        name {str} -- An author path in authors/
    """
    return path.join(config['journal_path'], 'content', 'authors', username)


def generate_author_content_path(username):
    """Returns the path where posts will be stored for a given author.
    
    Arguments:
        username {str} -- The author's username
    """
    return path.join(config['journal_path'], 'content', 'post', 'team',
                     username)


def create_author(username, name, avatar):
    """Creates a new author for the Journal instance.
    
    Arguments:
        username {str} -- The author's username
        name {str} -- The name of the author
        avatar {str} -- The filepath to an avatar image
    """
    if not username:
        username = config['username']
    click.secho('Setting up the author for {}'.format(username), fg='green')

    while not username:
        username = click.prompt("Username")
    author_path = generate_author_path(username)
    if path.exists(author_path):
        click.secho(
            'An author already exists at {}'.format(author_path), fg='red')
        return

    while not name:
        name = click.prompt("Name")
    while not avatar:
        avatar = click.prompt("Path to avatar image")
        avatar = path.expanduser(avatar)
        if not path.exists(avatar):
            click.secho(
                'The file at {} does not exist'.format(avatar), fg='yellow')
            avatar = None
    TEMPLATE_CONTEXT = {'username': username, 'name': name}

    _, avatar_extension = path.splitext(avatar)
    author_content_path = generate_author_content_path(username)
    author_md_path = path.join(author_path, '_index.md')
    author_avatar_path = path.join(author_path,
                                   'avatar{}'.format(avatar_extension))

    os.makedirs(author_path, exist_ok=True)
    os.makedirs(author_content_path, exist_ok=True)

    template_path = load_author_template()
    if not path.exists(template_path):
        click.secho(
            'No author template found at {}'.format(template_path), fg='red')
        return

    output = parse_template(template_path, TEMPLATE_CONTEXT)
    with open(author_md_path, 'w') as author_file:
        author_file.write(output)
    copyfile(avatar, author_avatar_path)
    click.secho('Created author at {}'.format(author_path), fg='green')


@click.command()
@click.argument('username', required=False)
@click.option('--name', required=False)
@click.option('--avatar', type=click.Path(exists=True))
def author(username, name, avatar):
    """Creates a new author for the Journal instance.
    """
    create_author(username, name, avatar)