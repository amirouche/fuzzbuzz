#!/usr/bin/env python
import os
from setuptools import setup
from setuptools import find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="fuzzyhash",
    version="0.3.0",
    author="Amirouche Boubekki",
    author_email="amirouche@hyper.dev",
    url="https://github.com/amirouche/fuzzyhash",
    description="fuzzy hash and distance for short strings.",
    long_description=read("README.md"),
    long_description_content_type='text/markdown',
    py_modules = ['fuzzyhash'],
    zip_safe=False,
    license="Apache 2.0",
    install_requires=["pyblake2"],
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering",
    ],
)
