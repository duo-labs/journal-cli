import os
import subprocess
import fnmatch
import click
import re

from jinja2 import Environment, FileSystemLoader

from config import config


def datetimefilter(value, format='%Y-%m-%d'):
    """Simple Jinja2 filter to convert datetime values to the desired format

    Arguments:
        value {datetime.datetime} -- The datetime value

    Keyword Arguments:
        format {str} -- The datetime format string (default: {'%Y-%m-%d'})

    Returns:
        str -- The datetime formatted according to the provided format string.
    """

    return value.strftime(format)


def get_last_modified(directory):
    """Returns the absolute path to the last modified file in the directory.

    Arguments:
        directory {str} -- The directory to search
    """
    # Unfortunately, Python < 3.5 doesn't have the glob recursive operator
    # so, according to StackOverflow, the best approach is to use a mix of
    # os.walk and fnmatch.filter. Seems reasonable.
    valid_files = []
    for root, _, files in os.walk(directory):
        # Get all the files in the directory that match one of the valid
        # extensions.
        for extension in config['templates']:
            if extension == 'daily_log':
                continue
            valid_files.extend(
                fnmatch.filter(
                    [os.path.join(root, filename) for filename in files],
                    '*{}'.format(extension)))

    return max(valid_files, key=os.path.getmtime)


def launch_editor(filepath):
    """Launches an editor with the provided filepath

    Arguments:
        filepath {str} -- The file to open in the configured editor
    """
    command = [config['editor'].get('command')]
    for arg in config['editor'].get('args'):
        command.append(arg.format(filepath))
    try:
        cmd = subprocess.Popen(command)
        cmd.wait()
    except OSError:
        if config['editor'].get('command') == "code":
            click.secho(
                "The 'code' editor was specified in your config file but it doesn't seem to be setup, have a look here for instuctions on how to fix that: ",
                nl=False,
                fg='red')
            click.secho(
                "https://code.visualstudio.com/docs/setup/mac#_launching-from-the-command-line"
            )
        else:
            click.secho(
                'Unknown editor "%s" specified, please check your configuration file'
                % (config['editor'].get('command')),
                fg='red')


def parse_template(filepath, ctx):
    """Parses a Jinja template from the provided filepath and context

    Arguments:
        filepath {str} -- The filepath to the Jinja template
        ctx {dict} -- Context to send to the template
    """
    # Setup the Jinja2 template environment
    env = Environment(loader=FileSystemLoader(os.path.dirname(filepath)))

    # Parse the Jinja2 template
    env.filters['strftime'] = datetimefilter
    j2_template = env.get_template(os.path.basename(filepath))
    output = j2_template.render(ctx)
    return output


def print_hugo_install_instructions():
    """Prints out instructions on how to install Hugo
    """
    click.secho(
        '''
    It appears that Hugo isn't installed, which is needed to
    launch the preview server.

    If you have Homebrew, you can install Hugo using "brew install hugo".
    Otherwise, you can get the binary from here:

        https://gohugo.io/getting-started/installing/.

    After you have Hugo installed and can run "hugo -h" successfully, try
    running "journal preview" again. If you run into any issues, reach out on 
    GitHub and we'll be happy to help.''',
        fg='yellow')


def generate_image_path(post_slug, filename):
    """Returns the default namespaced images path for a file.

    By default, it's recommended to store images in
    static/images/team/<username>/<post_slug>/, which is what this returns.

    Arguments:
        post_slug {str} -- The post slug to be used when building the path
        filename {str} -- The image filename

    Returns:
        str -- An absolute path to the images directory at
            static/images/team/<username>/<post_slug>/<filename>
    """
    return os.path.join(config['journal_path'], 'static', 'images', 'team',
                        config['username'], post_slug, filename)


def generate_post_path(filename):
    """Returns the default namespaced project path for a file.

    If the filename starts with "daily-log", we assume it's a daily log and
    move it one subdirectory lower into the "daily" directory for backwards
    compatibility.

    Arguments:
        filename {str} -- The filename of the post

    Returns:
        str -- A project path namespaced under team/<username>/<filename>
    """
    project_path = os.path.join(config['journal_path'], 'content', 'post',
                                'team/{}/'.format(config['username']))
    if filename.startswith('daily-log'):
        project_path = os.path.join(project_path, 'daily')
    project_path = os.path.join(project_path, filename)
    return project_path


def generate_slug(title):
    """Generates a filename slug from a title.

    This is the reverse of the typical slug -> title operation.

    Arguments:
        title {str} -- The post title
    """
    slug = title.lower()
    # Convert special characters
    slug = re.sub('[^a-zA-Z0-9\-_\.]', '-', slug)
    # Trim the end
    slug = re.sub('[^a-zA-Z0-9]+$', '', slug)
    return slug

def is_docker():
    """Returns whether or not Journal is being executed in Docker"""
    return os.environ.get('JOURNAL_DOCKER', False)