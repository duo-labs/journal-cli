import click
import subprocess

from os import path

from config import config


@click.command()
def update():
    """Updates the journal CLI.

    The updates work by pulling the latest changes from Github.
    """
    repo_path = path.abspath(path.join(path.dirname(__file__), '../'))
    try:
        subprocess.check_output(['git', 'pull', '--rebase'], cwd=repo_path)
        click.secho('journal client successfully updated!', fg='green')

        subprocess.check_output([
            'git', 'submodule', 'update', '--init', '--remote', '--recursive'
        ],
                                cwd=config['journal_path'])
        click.secho('Journal theme successfully updated!', fg='green')
    except Exception as e:
        click.secho(str(e), fg='red')
        return