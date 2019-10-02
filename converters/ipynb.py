from os import path, makedirs

import click

from config import config
from commands.util import generate_image_path, generate_post_path

IPYNB_TEMPLATE = '''
{%- extends 'markdown.tpl' -%}

{% block data_text scoped %}
```ipynb-output
{{ output.data['text/plain']}}
```
{% endblock data_text %}

{% block stream %}
```ipynb-output
{{ output.text}}
```
{% endblock stream %}
'''


class IpynbConverter:
    def __init__(self, filepath):
        self.filepath = filepath
        self.post_slug, _ = path.splitext(path.basename(self.filepath))

    def save_image(self, image_name, content):
        """Saves an image to the correct directory

        Arguments:
            image_name {str} -- The filename of the image
            content {bytes} -- The raw image bytes
        """
        image_path = generate_image_path(self.post_slug, image_name)
        makedirs(path.dirname(image_path), exist_ok=True)
        click.secho('Saving image to {}'.format(image_path), fg='green')
        with open(image_path, 'wb') as image_output:
            image_output.write(content)

    def convert(self):
        """Converts a Jupyter notebook for use in Journal.

        Specifically, this function:
        """
        import nbformat
        from traitlets.config import Config
        from nbconvert import MarkdownExporter

        notebook = nbformat.read(self.filepath, as_version=4)
        # Determine the static folder path and configure the Config
        c = Config()
        c.ExtractOutputPreprocessor.output_filename_template = path.join(
            '/images', 'team', config['username'], self.post_slug,
            '{unique_key}_{cell_index}_{index}{extension}')
        exporter = MarkdownExporter(config=c, raw_template=IPYNB_TEMPLATE)
        post, images = exporter.from_notebook_node(notebook)
        for image_path, content in images['outputs'].items():
            image_name = path.basename(image_path)
            self.save_image(image_name, content)
        new_filename = '{}.md'.format(self.post_slug)
        post_path = generate_post_path(new_filename)
        click.secho('Saving post content to {}'.format(post_path), fg='green')
        with open(post_path, 'w') as output:
            output.write(post)
        return post_path