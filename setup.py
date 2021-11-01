"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import setuptools

setuptools.setup(
    name='label_studio_sdk',
    version='0.0.1',
    author='Heartex',
    author_email="hello@heartex.ai",
    description='Label Studio annotation tool',
    long_description='Label Studio Python SDK',
    long_description_content_type='text/markdown',
    url='https://github.com/heartexlabs/label-studio',
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6'
)
