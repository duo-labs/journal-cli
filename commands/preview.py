import click
import subprocess

from distutils.spawn import find_executable

from config import config
from .util import print_hugo_install_instructions, is_docker

HUGO_COMMAND = 'hugo'


@click.command()
@click.option(
    '--drafts', '-D', default=True, help='Whether to render draft posts')
def preview(drafts):
    """Launches Hugo's preview server to live reload pages.

    If the Hugo executable isn't found on the PATH, then we'll provide some
    installation instructions showing how best to install it.
    """
    if not find_executable(HUGO_COMMAND):
        print_hugo_install_instructions()
        return
    command = ['hugo', 'server']
    if drafts:
        command.append('-D')
    if is_docker():
        command.extend(['--bind', '0.0.0.0'])
    try:
        cmd = subprocess.Popen(command, cwd=config['journal_path'])
        cmd.wait()
    except OSError as e:
        click.secho(
            'Something went wrong when running "{}": {}'.format(
                ' '.join(cmd), e),
            fg='red')
