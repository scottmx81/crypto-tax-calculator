#!/usr/bin/env python
from glob import glob
from os.path import basename, splitext
from setuptools import setup, find_packages


setup(
    name='crypto_taxes',
    version='0.1',
    description='Crypto tax calculator.',
    url='http://github.com/scottmx81/crypto-tax-calculator/',
    author='Scott Mountenay',
    author_email='scott@canadiense.net',
    license='MIT',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False
)
