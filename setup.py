"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import re
import setuptools

# Module dependencies
requirements, dependency_links = [], []
with open('requirements.txt') as f:
    for line in f.read().splitlines():
        requirements.append(line)

with open('label_studio_sdk/__init__.py') as f:
    version = re.search("__version__ ?= ?'(.*?)'", f.read()).group(1)

setuptools.setup(
    name='label-studio-sdk',
    version=version,
    author='Heartex',
    author_email="hello@heartex.ai",
    description='Label Studio annotation tool',
    long_description='Label Studio Python SDK',
    long_description_content_type='text/markdown',
    url='https://github.com/heartexlabs/label-studio-sdk',
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=requirements
)
