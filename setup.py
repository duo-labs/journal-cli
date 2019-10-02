from setuptools import setup, find_packages

setup(
    name='journal',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'alembic', 'blinker', 'click', 'colorama', 'enum34', 'Flask',
        'Flask-Login', 'Flask-Mail', 'Flask-Migrate', 'Flask-Principal',
        'Flask-SQLAlchemy', 'future', 'gitdb2', 'GitPython', 'gunicorn',
        'inflection', 'itsdangerous', 'Jinja2', 'knowledge_repo', 'Mako',
        'Markdown', 'MarkupSafe', 'Pygments', 'python-dateutil',
        'python-editor', 'PyYAML', 'six', 'smmap2', 'SQLAlchemy', 'tabulate',
        'toml', 'Werkzeug', 'wheel'
    ],
    entry_points='''
        [console_scripts]
        journal=journal:cli
    ''',
    package_data={'journal': ['templates/*', 'journal.toml']})
