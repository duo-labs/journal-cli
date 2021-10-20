import git
import json
import click
import subprocess

try:
    from urllib.request import Request, urlopen
except ImportError:
    from urllib2 import Request, urlopen

from os import path
from datetime import datetime

from constants import FORTUNE_API_URL, POST_DIRECTORY
from config import config
from commands.util import get_last_modified
from converters import convert_file


def generate_commit_message(filename):
    """Returns a generic commit message.

    Arguments:
        filename {str} -- The absolute path to the added file

    Returns:
        str -- The generated commit message
    """

    filename = path.basename(filename)
    return 'Update to {} from {} at {} UTC'.format(filename,
                                                   config['username'],
                                                   datetime.now())


def deploy_git(filepath):
    """Performs the traditional git merge/push dance.
    """

    repo = git.Repo(config['journal_path'])
    static_path = path.join(config['journal_path'], 'static/images')
    # Commit the changes
    repo.index.add([filepath, static_path])
    # List the files being committed
    for diff in repo.index.diff("HEAD"):
        click.secho('[+] Adding {}'.format(diff.a_path), fg='green')
    repo.index.commit(generate_commit_message(filepath))
    # Pull the latest from upstream
    subprocess.check_output(['git', 'checkout', 'main'],
                            cwd=config['journal_path'])
    subprocess.check_output(['git', 'pull', '--rebase'],
                            cwd=config['journal_path'])
    subprocess.check_output(['git', 'push'], cwd=config['journal_path'])


@click.command()
@click.argument('filename', required=False)
def push(filename):
    """Pushes the post to Journal.

    Push adds the note to the actual Git repo, and deploys it
    using the standard pull/merge/push Git workflow.

    By default, if the `filename` argument isn't provided, the last modified
    file is deployed.
    """

    # Determine the correct filename to use based on the arguments
    if not filename:
        filename = get_last_modified(
            path.join(config.get('journal_path'), POST_DIRECTORY))
    elif not path.isabs(filename):
        filename = path.abspath(
            path.join(config.get('journal_path'), POST_DIRECTORY, filename))

    if not path.exists(filename):
        click.secho('Post "{}" not found'.format(filename), fg='red')
        return

    post_filepath = path.relpath(
        filename, path.join(config.get('journal_path'), POST_DIRECTORY))

    # Before we do anything, let's confirm that this is what the user is
    # expecting to do.
    if not click.confirm(
            click.style('Push {}?'.format(post_filepath), fg='yellow')):
        return

    click.secho('Pushing to the Journal', fg='green')
    try:
        filename = convert_file(filename)
        deploy_git(filename)
        if not config.get('fortune', False):
            click.secho(
                'Push successful! You should be good to go.', fg='green')
        else:
            # Let's get you a fortune cuz you just dropped KNOWLEDGE!
            request = Request(
                FORTUNE_API_URL,
                data=None,
                headers={
                    'User-Agent':
                    'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'
                })
            try:
                fortune = urlopen(request).read().decode('utf-8')
            except Exception as e:
                fortune = ":-( Lame, error getting your fortune. Guess it's not your lucky day. (%s)" % (
                    e)
            click.secho(
                "Push successful! Here's your fortune...\n\t'%s'" %
                (json.loads(fortune).strip()),
                fg='green')
    except Exception as e:
        click.secho('Error: {}'.format(e))
