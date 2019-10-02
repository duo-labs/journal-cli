from os import path, makedirs
from datetime import datetime

import yaml
import click
import sys
import os
import shutil

from commands.util import generate_image_path, generate_post_path, generate_slug
from config import config

YAML_WHITELIST = ['authors', 'author', 'title', 'tags', 'date', 'draft']
YAML_BOUNDARY = '---'


class RmdConverter:
    """A converter for [name].rmd files.

    This converter works by assuming that another file in the same directory
    exists called [name]_blogdown.html. We take that HTML file, copy the
    front matter from the Rmd file into it, and move it to the correct location.

    Next, we copy over any images in the [name]_files/ directory into the
    correct location in Journal. We then update links to those images within
    the HTML file to point to the right location, making sure that the images
    will load correctly.

    (TODO) Missing some images in the test files?

    (TODO) Finally, we copy over the Rmd file itself into the static folder,
    creating a link between the two.
    """

    def __init__(self, filepath):
        """Creates a new instance of the RmdConverter

        Arguments:
            filename {str} -- The absolute path to the Rmd file to convert.
        """
        self.filepath = filepath
        self.source_folder = path.abspath(path.dirname(self.filepath))
        # Filename serves as a predictable prefix which is the same across the
        # [prefix].Rmd file, the [prefix]_blogdown.html file, and the
        # [prefix]_files/ folder.
        self.filename, _ = path.splitext(path.basename(self.filepath))
        self.rmd_file = path.join(self.source_folder,
                                  '{}.Rmd'.format(self.filename))
        self.blogdown_file = path.join(
            self.source_folder, '{}_blogdown.html'.format(self.filename))

    def copy_images(self, post_slug):
        """Copies the figures and images into Journal

        This is a pretty naive approach right now. It just looks for files in
        the top-level report_files/figure-html/ directory and copies those
        over to the static images directory.

        It's possible we'll need to adjust this later.

        Arguments:
            post_slug {str} -- The post slug used when creating the
                destination filename
        """
        image_source_directory = path.join('{}_files'.format(self.filename),
                                           'figure-html')
        for dirpath, _, images in os.walk(
                path.join(self.source_folder, image_source_directory)):
            for image in images:
                image_destination = generate_image_path(post_slug, image)
                image_path = path.abspath(path.join(dirpath, image))
                makedirs(path.dirname(image_destination), exist_ok=True)
                shutil.copy(image_path, image_destination)

    def load_front_matter(self):
        """Loads the front matter from the Rmd file
        """
        raw_yaml = ''
        with open(self.rmd_file, 'r') as rmd:
            for line in rmd.readlines():
                # Check if this is the ending tag
                if line.strip() == YAML_BOUNDARY:
                    if raw_yaml:
                        break
                raw_yaml += line
        front_matter = yaml.load(raw_yaml)
        # Trim the YAML to only the keys Hugo is known to support
        front_matter = {
            k: v
            for (k, v) in front_matter.items() if k in YAML_WHITELIST
        }
        # Manually fix the conversion to an authors array if only the author
        # key is provided.
        if not front_matter.get('authors') and front_matter.get('author'):
            front_matter['authors'] = [front_matter['author']]
            del front_matter['author']
        return front_matter

    def validate(self):
        """Validates that the correct files are available before attempting
        the converstion.
        """
        for filename in [self.rmd_file, self.blogdown_file]:
            if not path.exists(path.join(self.source_folder, filename)):
                click.secho('Missing file: {}'.format(filename), fg='red')
                sys.exit(1)

    def generate_blogdown_html(self, img_dir):
        from bs4 import BeautifulSoup
        with open(self.blogdown_file, 'r') as html:
            soup = BeautifulSoup(html.read(), "html.parser")
        files_dir = '{}_files'.format(self.filename)
        # Update links to images to point to the new path
        for img in soup.find_all('img'):
            if not img['src'].startswith(files_dir):
                continue
            img['src'] = img['src'].replace(
                '{}/figure-html/'.format(files_dir), '')
            img['src'] = path.join(img_dir, img['src'])
        return str(soup)

    def convert(self):
        """Converts an Rmd file for Journal.
        """
        self.validate()
        # Generate the slug from the title in the metadata
        front_matter = self.load_front_matter()
        front_matter['date'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        if not front_matter.get('title'):
            click.secho(
                'Invalid front matter in Rmd file: missing "title" field',
                fg='red')
            sys.exit(1)
        post_slug = generate_slug(front_matter['title'])
        post_filename = '{}.html'.format(post_slug)
        post_path = generate_post_path(post_filename)
        # Copy the image assets
        self.copy_images(post_slug)
        img_html_src_dir = path.join('/images', 'team', config['username'],
                                     post_slug)
        with open(post_path, 'w') as post:
            # Copy the metadata
            post.write('---\n{}---'.format(
                yaml.dump(front_matter, default_flow_style=False)))
            # Generate the HTML, adjusting the image paths to point to the right
            # location
            html = self.generate_blogdown_html(img_html_src_dir)
            post.write(html)
        return post_path
