from commands.cli import cli
from commands.convert import convert
from commands.create import create
from commands.preview import preview
from commands.push import push
from commands.update import update
from commands.dataset import dataset
from commands.author import author

cli.add_command(author)
cli.add_command(convert)
cli.add_command(create)
cli.add_command(preview)
cli.add_command(push)
cli.add_command(update)
cli.add_command(dataset)
