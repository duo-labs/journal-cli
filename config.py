from os import environ, path

import click
import getpass
import toml
import shutil
import sys
import subprocess

import git

from constants import JOURNAL_UPSTREAM

SETUP_REPOSITORY_MESSAGE = """
    It looks like this is your first time using Journal.

    To set things up, it's assumed you've already made a fork or clone
    of the Git repository at {}.

    What is the URL of your repository?""".format(JOURNAL_UPSTREAM)

SETUP_JOURNAL_PATH_MESSAGE = """
    Next, we'll get a local clone of this repository. This is where your
    posts will be stored.

    Where would you like this repository cloned to?"""

SETUP_CONFIRMATION_MESSAGE = """
    You're all set! You can create your first author using:

    journal author"""


def load_default_config():
    """Loads and returns the default configuration as a dict
    
    Returns:
        dict -- The loaded configuration
    """
    config_file = path.abspath(
        path.join(path.dirname(__file__), 'journal.toml'))
    return toml.load(config_file)


def setup_config(config_path, config):
    """Validates the configuration and fills in missing metadata.

    Arguments:
        content {dict} -- The initial loaded configuration
    """
    # If the journal_path exists, then we're probably good.
    if config.get('journal_path'):
        return config

    # Then, we'll clone the repo
    click.secho(SETUP_REPOSITORY_MESSAGE, fg='green')
    journal_path = environ.get('JOURNAL_PATH', '')
    repo_url = environ.get('JOURNAL_REPO', '')
    while not repo_url:
        repo_url = click.prompt("Repository URL")
    config['upstream_repo'] = repo_url
    while not journal_path:
        journal_path = path.expanduser(click.prompt("Path"))
        dir_name, _ = path.split(journal_path)

        if not path.exists(dir_name):
            click.secho(
                'Directory does not exist: {}'.format(journal_path),
                fg='yellow')
            journal_path = ""
    config['journal_path'] = journal_path
    try:
        # Check if we need to clone the repo - this catches the case where may
        # already have Journal cloned
        repo = git.Repo(config['journal_path'])
        if repo.remote().url != config['upstream_repo']:
            click.secho(
                'Repository exists, but isn\'t pointing to {}'.format(
                    config['upstream_repo']),
                fg='red')
    except Exception as e:
        try:
            click.secho(
                'Cloning from {} to {}'.format(config['upstream_repo'],
                                               config['journal_path']),
                fg='green')
            # Using subprocess instead of GitPython to properly handle tracking
            # progress since this can take a bit of time.
            subprocess.check_output(
                ['git', 'clone', config['upstream_repo'], journal_path])
            subprocess.check_output(['git', 'submodule', 'update', '--init'],
                                    cwd=config['journal_path'])
        except Exception as e:
            click.secho('Error cloning repo: {}'.format(e), fg='red')
            sys.exit(1)

    # Fallback to the correct username if not specified
    if not config.get('username'):
        config['username'] = environ.get('JOURNAL_USER', getpass.getuser())

    # Save the config
    click.secho(
        'Saving new configuration to: {}'.format(config_path), fg='green')
    with open(config_path, 'w') as config_output:
        config_output.write(toml.dumps(config))

    click.secho(SETUP_CONFIRMATION_MESSAGE, fg='green')
    return config


def load_config(config_path=None):
    if config_path is None:
        config_path = environ.get(
            'JOURNAL_CONFIG', path.join(path.expanduser('~'), '.journal.toml'))

    if not path.exists(config_path):
        click.secho(
            'Configuration not found at "{}"'.format(config_path), fg='yellow')
        shutil.copy(
            path.abspath(path.join(path.dirname(__file__), 'journal.toml')),
            config_path)

    with open(config_path) as f:
        return setup_config(config_path, toml.load(f))


config = load_config()
