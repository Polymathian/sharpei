#!/usr/bin/env python
import os
import re

from setuptools import setup, find_packages


ROOT = os.path.dirname(__file__)
VERSION_RE = re.compile(r'''__version__ = ['"]([0-9.]+)['"]''')


requires = [
    'boto3==1.13.16',
    'click==7.1.2',
    'watchdog==0.10.2',
]


def get_version():
    init = open(os.path.join(ROOT, 'sharpei', '__init__.py')).read()
    return VERSION_RE.search(init).group(1)


setup(
    name='sharpei',
    version=get_version(),
    description='Watchdog to sync file changes to AWS S3',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author='Polymathian',
    url='https://github.com/polymathian/sharpei',
    packages=find_packages(exclude=['test*']),
    include_package_data=True,
    install_requires=requires,
    entry_points={
        'console_scripts': [
            'sharpei = sharpei.cli:main'
        ]
    },
    python_requires='>=3.6',
    license="Apache License 2.0",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: System :: Archiving',
        'Typing :: Typed',
    ],
)
