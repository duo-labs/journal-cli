from os import path

import click

from .ipynb import IpynbConverter
from .rmd import RmdConverter

CONVERTERS = {'.ipynb': IpynbConverter, '.rmd': RmdConverter}


class ConversionError(Exception):
    """A generic error for known conversion errors"""
    pass


def convert_file(filepath):
    """Applies the correct converter depending on the filetype.

    Arguments:
        filepath {str} -- The absolute path to the file that needs to be
        converted

    Returns:
        str -- The converted filename to be used for further operations (like
        pushing)
    """
    _, ext = path.splitext(filepath.lower())
    if ext == '.md':
        return filepath
    if ext not in CONVERTERS:
        raise ConversionError(
            "We don't have a way to convert {} files yet".format(ext))
    try:
        converter_cls = CONVERTERS[ext]
        converter = converter_cls(filepath)
        return converter.convert()
    except Exception as e:
        raise ConversionError('Error converting {}: {}'.format(filepath, e))
