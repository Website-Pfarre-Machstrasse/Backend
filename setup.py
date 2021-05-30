from os import path

from setuptools import setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='Website-Pfarre-Machstrasse-Backend',
    version='0.1.0',
    packages=['server',
              'server.common',
              'server.common.doc',
              'server.common.jwt',
              'server.common.util',
              'server.common.schema',
              'server.common.database',
              'server.resources'],
    url='https://github.com/Website-Pfarre-Machstrasse/Backend',
    author='Georg Burkl',
    author_email='minecraftschurli@gmail.com',
    description='',
    long_description=long_description,
    long_description_content_type='text/markdown',
    scripts=['./backup.sh', './restore.sh', './start.sh'],
    install_requires=[
        'flask',
        'flask-bcrypt',
        'flask-sqlalchemy',
        'flask-restful',
        'flask-apispec',
        'flask-cors',
        'flask-jwt-extended',
        'flask-tinify',
        'flask-marshmallow',
        'marshmallow-sqlalchemy',
        'marshmallow',
        'marshmallow-enum',
        'diff-match-patch',
        'pyyaml'
    ]
)
